# inventory/management/commands/cron_wol_proxy.py
from django.core.management.base import BaseCommand
from inventory.models import WolProxy
import socket
import struct


class Command(BaseCommand):
    help = 'Check WOL proxy status and send magic packets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--proxy-id',
            type=int,
            help='Specific proxy ID to check',
        )

    def handle(self, *args, **options):
        proxy_id = options.get('proxy_id')
        
        if proxy_id:
            proxies = WolProxy.objects.filter(id=proxy_id)
        else:
            proxies = WolProxy.objects.all()

        for proxy in proxies:
            self.stdout.write(f"Checking proxy: {proxy.name}")
            # Check if proxy is online
            is_online = self.check_proxy_online(proxy.entity.ip_address)
            
            if is_online:
                self.stdout.write(
                    self.style.SUCCESS(f"Proxy {proxy.name} is online")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Proxy {proxy.name} is OFFLINE")
                )

    def check_proxy_online(self, ip_address):
        """Check if proxy is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip_address, 9))  # Port 9 for WOL
            sock.close()
            return result == 0
        except Exception as e:
            return False

    def send_magic_packet(self, mac_address, broadcast_ip='255.255.255.255'):
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
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error sending magic packet: {e}")
            )
            return False
