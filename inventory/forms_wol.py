# -*- coding: utf-8 -*-
"""
Wake-on-LAN Proxy Forms
"""

from django import forms
from django.core.validators import validate_ipv4_address
from django.utils.translation import gettext_lazy as _
import re

from inventory.models import WOLProxy


class WOLProxyForm(forms.ModelForm):
    """
    Form for creating and editing WOL Proxy configurations
    """
    
    class Meta:
        model = WOLProxy
        fields = ['name', 'address', 'port', 'subnets', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Proxy Server Name'),
                'required': 'required'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('192.168.1.1 or proxy.example.com'),
                'required': 'required'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '9',
                'min': '1',
                'max': '65535',
                'required': 'required'
            }),
            'subnets': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': _('192.168.1.0/24, 10.0.0.0/8'),
                'required': 'required'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': _('Proxy Name'),
            'address': _('Proxy Address'),
            'port': _('Port Number'),
            'subnets': _('Managed Subnets'),
            'is_active': _('Active')
        }
        help_texts = {
            'name': _('A descriptive name for this WOL proxy server'),
            'address': _('IP address or hostname of the proxy server'),
            'port': _('Port number for WOL service (default: 9)'),
            'subnets': _('Comma-separated list of subnets in CIDR notation'),
            'is_active': _('Enable or disable this proxy')
        }
    
    def clean_address(self):
        """
        Validate the proxy address (IP or hostname)
        """
        address = self.cleaned_data.get('address')
        if not address:
            raise forms.ValidationError(_('Proxy address is required'))
        
        # Try to validate as IPv4
        try:
            validate_ipv4_address(address)
            return address
        except forms.ValidationError:
            pass
        
        # Validate as hostname
        hostname_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
            r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        
        if not hostname_pattern.match(address):
            raise forms.ValidationError(
                _('Enter a valid IP address or hostname')
            )
        
        return address
    
    def clean_port(self):
        """
        Validate the port number
        """
        port = self.cleaned_data.get('port')
        if port is None:
            raise forms.ValidationError(_('Port number is required'))
        
        if not (1 <= port <= 65535):
            raise forms.ValidationError(
                _('Port number must be between 1 and 65535')
            )
        
        return port
    
    def clean_subnets(self):
        """
        Validate and normalize subnet list
        """
        subnets_raw = self.cleaned_data.get('subnets')
        if not subnets_raw:
            raise forms.ValidationError(_('At least one subnet is required'))
        
        # Split by comma and clean whitespace
        subnets = [s.strip() for s in subnets_raw.split(',') if s.strip()]
        
        if not subnets:
            raise forms.ValidationError(_('At least one subnet is required'))
        
        # Validate each subnet in CIDR notation
        cidr_pattern = re.compile(
            r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/'
            r'(?:3[0-2]|[12]?[0-9])$'
        )
        
        valid_subnets = []
        for subnet in subnets:
            if not cidr_pattern.match(subnet):
                raise forms.ValidationError(
                    _('Invalid subnet format: %(subnet)s. Use CIDR notation (e.g., 192.168.1.0/24)'),
                    params={'subnet': subnet}
                )
            valid_subnets.append(subnet)
        
        # Return as comma-separated string
        return ', '.join(valid_subnets)
    
    def clean(self):
        """
        Additional form-level validation
        """
        cleaned_data = super().clean()
        
        # Check for duplicate proxy address
        address = cleaned_data.get('address')
        port = cleaned_data.get('port')
        
        if address and port:
            existing = WOLProxy.objects.filter(
                address=address,
                port=port
            )
            
            # Exclude current instance when editing
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(
                    _('A proxy with this address and port already exists')
                )
        
        return cleaned_data
