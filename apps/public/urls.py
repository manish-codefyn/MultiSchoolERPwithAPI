from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('institutions/', views.TenantListView.as_view(), name='tenant_list'),
    path('institutions/<slug:schema_name>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    path('api/public/demo-request/', views.DemoRequestView.as_view(), name='demo_request'),
]
