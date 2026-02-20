# Modern UI URL patterns - namespace: 'modern'
# Include this in the main urls.py with:
#   path('modern/', include('updatengine.urls_modern', namespace='modern'))

from django.urls import path
from . import views_modern

app_name = 'modern'

urlpatterns = [
    # Dashboard
    path('dashboard/', views_modern.dashboard, name='dashboard'),

    # Inventory / Parc
    path('inventory/', views_modern.inventory_view, name='inventory'),
    path('machine/<int:machine_id>/', views_modern.machine_detail, name='machine_detail'),

    # HTMX partials
    path('api/dashboard-stats/', views_modern.htmx_dashboard_stats, name='dashboard_stats'),
    path('api/machine-search/', views_modern.api_machine_search, name='machine_search'),

    # Deploy
    path('deploy/', views_modern.deploy_overview, name='deploy'),

    # Alerting & Rapports
    path('alerts/', views_modern.alerts_view, name='alerts'),
    path('api/alert-badge/', views_modern.htmx_alert_badge, name='alert_badge'),
    path('api/alerts-rows/', views_modern.htmx_alerts_rows, name='alerts_rows'),
    path('api/alert-count/', views_modern.api_alert_count, name='alert_count'),
]
