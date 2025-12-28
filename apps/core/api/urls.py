from django.urls import path
from apps.core.api.views import (
    DashboardAPIView,
    GlobalSearchAPIView
)

urlpatterns = [
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('search/', GlobalSearchAPIView.as_view(), name='global-search'),
]
