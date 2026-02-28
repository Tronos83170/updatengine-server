# -*- coding: utf-8 -*-
"""
Wake-on-LAN Proxy URL Configuration
"""

from django.urls import path
from inventory import views_wol

urlpatterns = [
    # WOL Proxy Management
    path('wol/proxies/', 
         views_wol.wol_proxy_list, 
         name='wol_proxy_list'),
    
    path('wol/proxies/add/', 
         views_wol.wol_proxy_add, 
         name='wol_proxy_add'),
    
    path('wol/proxies/<int:proxy_id>/edit/', 
         views_wol.wol_proxy_edit, 
         name='wol_proxy_edit'),
    
    path('wol/proxies/<int:proxy_id>/delete/', 
         views_wol.wol_proxy_delete, 
         name='wol_proxy_delete'),
]
