from django.urls import path
from apps.certificates import views

app_name = 'certificates'

urlpatterns = [
    path('', views.CertificateListView.as_view(), name='certificate_list'),
    path('create/', views.CertificateCreateView.as_view(), name='certificate_create'),
    path('bulk-create/', views.BulkCertificateCreateView.as_view(), name='certificate_bulk_create'),
    path('<uuid:pk>/', views.CertificateDetailView.as_view(), name='certificate_detail'),
    path('<uuid:pk>/download/', views.CertificateDownloadView.as_view(), name='certificate_download'),
    path('<uuid:pk>/edit/', views.CertificateUpdateView.as_view(), name='certificate_update'),
    path('<uuid:pk>/delete/', views.CertificateDeleteView.as_view(), name='certificate_delete'),
]
