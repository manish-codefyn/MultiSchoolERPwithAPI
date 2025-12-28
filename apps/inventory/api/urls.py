from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categorys', views.CategoryViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'items', views.ItemViewSet)
router.register(r'stockmovements', views.StockMovementViewSet)
router.register(r'purchaseorders', views.PurchaseOrderViewSet)
router.register(r'purchaseorderitems', views.PurchaseOrderItemViewSet)
router.register(r'issuerequests', views.IssueRequestViewSet)
router.register(r'issueitems', views.IssueItemViewSet)
router.register(r'assets', views.AssetViewSet)
router.register(r'maintenancerecords', views.MaintenanceRecordViewSet)
router.register(r'inventoryreports', views.InventoryReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
