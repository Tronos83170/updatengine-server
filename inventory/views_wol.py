# inventory/views_wol.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from inventory.models import WolProxy, Entity
import socket
import struct


@login_required
def wol_proxy_list(request):
    """List all WOL proxies"""
    proxies = WolProxy.objects.select_related('entity').all()
    
    # Check status for each proxy
    for proxy in proxies:
        proxy.is_online = check_proxy_status(proxy.entity.ip_address)
    
    context = {
        'proxies': proxies,
        'title': 'WOL Proxies Management'
    }
    return render(request, 'inventory/wol_proxy_list.html', context)


@login_required
def wol_proxy_create(request):
    """Create a new WOL proxy"""
    if request.method == 'POST':
        entity_id = request.POST.get('entity')
        name = request.POST.get('name')
        
        try:
            entity = Entity.objects.get(id=entity_id)
            WolProxy.objects.create(
                entity=entity,
                name=name
            )
            messages.success(request, f'WOL Proxy "{name}" created successfully')
            return redirect('wol_proxy_list')
        except Exception as e:
            messages.error(request, f'Error creating WOL proxy: {e}')
    
    entities = Entity.objects.all()
    context = {
        'entities': entities,
        'title': 'Create WOL Proxy'
    }
    return render(request, 'inventory/wol_proxy_form.html', context)


@login_required
def wol_proxy_edit(request, pk):
    """Edit an existing WOL proxy"""
    proxy = get_object_or_404(WolProxy, pk=pk)
    
    if request.method == 'POST':
        entity_id = request.POST.get('entity')
        name = request.POST.get('name')
        
        try:
            entity = Entity.objects.get(id=entity_id)
            proxy.entity = entity
            proxy.name = name
            proxy.save()
            messages.success(request, f'WOL Proxy "{name}" updated successfully')
            return redirect('wol_proxy_list')
        except Exception as e:
            messages.error(request, f'Error updating WOL proxy: {e}')
    
    entities = Entity.objects.all()
    context = {
        'proxy': proxy,
        'entities': entities,
        'title': 'Edit WOL Proxy'
    }
    return render(request, 'inventory/wol_proxy_form.html', context)


@login_required
def wol_proxy_delete(request, pk):
    """Delete a WOL proxy"""
    proxy = get_object_or_404(WolProxy, pk=pk)
    
    if request.method == 'POST':
        name = proxy.name
        proxy.delete()
        messages.success(request, f'WOL Proxy "{name}" deleted successfully')
        return redirect('wol_proxy_list')
    
    context = {
        'proxy': proxy,
        'title': 'Delete WOL Proxy'
    }
    return render(request, 'inventory/wol_proxy_confirm_delete.html', context)


@login_required
def wol_proxy_check_status(request, pk):
    """Check WOL proxy status via AJAX"""
    proxy = get_object_or_404(WolProxy, pk=pk)
    is_online = check_proxy_status(proxy.entity.ip_address)
    
    return JsonResponse({
        'status': 'online' if is_online else 'offline',
        'proxy_id': pk,
        'proxy_name': proxy.name,
        'ip_address': proxy.entity.ip_address
    })


@login_required
def wol_send_packet(request, pk):
    """Send WOL packet to a machine via proxy"""
    if request.method == 'POST':
        machine_id = request.POST.get('machine_id')
        
        try:
            from inventory.models import Machine
            machine = Machine.objects.get(id=machine_id)
            proxy = WolProxy.objects.get(pk=pk)
            
            # Send magic packet
            success = send_magic_packet(
                machine.mac_address,
                proxy.entity.ip_address
            )
            
            if success:
                messages.success(
                    request,
                    f'WOL packet sent to {machine.name} via {proxy.name}'
                )
            else:
                messages.error(request, 'Failed to send WOL packet')
                
        except Exception as e:
            messages.error(request, f'Error: {e}')
        
        return redirect('wol_proxy_list')
    
    return JsonResponse({'error': 'POST required'}, status=400)


def check_proxy_status(ip_address):
    """Check if proxy is reachable"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip_address, 9))
        sock.close()
        return result == 0
    except Exception:
        return False


def send_magic_packet(mac_address, broadcast_ip='255.255.255.255'):
    """Send WOL magic packet"""
    try:
        # Remove separators from MAC address
        mac = mac_address.replace(':', '').replace('-', '')
        
        # Create magic packet
        data = b'FF' * 6 + (mac * 16).encode()
        packet = b''
        
        for i in range(0, len(data), 2):
            packet += struct.pack('B', int(data[i:i+2], 16))
        
        # Send packet
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast_ip, 9))
        sock.close()
        
        return True
    except Exception:
        return False
