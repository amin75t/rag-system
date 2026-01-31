"""
URL configuration for utils app.
"""
from django.urls import path
from .views import test_api, convert_miladi_to_samci, convert_samci_to_miladi

app_name = 'utils'

urlpatterns = [
    path('test-api/', test_api, name='test_api'),
    path('miladi-to-samci/', convert_miladi_to_samci, name='miladi_to_samci'),
    path('samci-to-miladi/', convert_samci_to_miladi, name='samci_to_miladi'),
]
