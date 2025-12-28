from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rolepermissions', views.RolePermissionViewSet)
router.register(r'apitokens', views.APITokenViewSet)
router.register(r'securityevents', views.SecurityEventViewSet)
router.register(r'loginattempts', views.LoginAttemptViewSet)

urlpatterns = [
    path('api-login/', views.CustomTokenObtainPairView.as_view(), name='api_login'),
    path('api-logout/', views.APILogoutView.as_view(), name='api_logout'),
    path('', include(router.urls)),
]
