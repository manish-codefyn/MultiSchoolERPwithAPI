from django.urls import path
from . import views

urlpatterns = [
    path('lookup/', views.TenantLookupView.as_view(), name='tenant_lookup'),
]
