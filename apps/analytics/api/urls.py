from django.urls import path
from apps.analytics.api.views import (
    AuditAnalysisReportListCreateAPIView, AuditAnalysisReportDetailAPIView,
    AuditPatternListCreateAPIView, AuditPatternDetailAPIView,
    AuditAlertListCreateAPIView, AuditAlertDetailAPIView,
    AuditDashboardListCreateAPIView, AuditDashboardDetailAPIView,
    AuditMetricListCreateAPIView, AuditMetricDetailAPIView,
    AuditMetricValueListCreateAPIView, AuditMetricValueDetailAPIView,
    DataSourceListCreateAPIView, DataSourceDetailAPIView,
    KPIModelListCreateAPIView, KPIModelDetailAPIView
)

urlpatterns = [
    # Audit Reports
    path('reports/', AuditAnalysisReportListCreateAPIView.as_view(), name='auditanalysisreport-list'),
    path('reports/<uuid:pk>/', AuditAnalysisReportDetailAPIView.as_view(), name='auditanalysisreport-detail'),

    # Patterns
    path('patterns/', AuditPatternListCreateAPIView.as_view(), name='auditpattern-list'),
    path('patterns/<uuid:pk>/', AuditPatternDetailAPIView.as_view(), name='auditpattern-detail'),

    # Alerts
    path('alerts/', AuditAlertListCreateAPIView.as_view(), name='auditalert-list'),
    path('alerts/<uuid:pk>/', AuditAlertDetailAPIView.as_view(), name='auditalert-detail'),

    # Dashboards
    path('dashboards/', AuditDashboardListCreateAPIView.as_view(), name='auditdashboard-list'),
    path('dashboards/<uuid:pk>/', AuditDashboardDetailAPIView.as_view(), name='auditdashboard-detail'),

    # Metrics
    path('metrics/', AuditMetricListCreateAPIView.as_view(), name='auditmetric-list'),
    path('metrics/<uuid:pk>/', AuditMetricDetailAPIView.as_view(), name='auditmetric-detail'),

    path('metric-values/', AuditMetricValueListCreateAPIView.as_view(), name='auditmetricvalue-list'),
    path('metric-values/<uuid:pk>/', AuditMetricValueDetailAPIView.as_view(), name='auditmetricvalue-detail'),

    # Data Sources
    path('datasources/', DataSourceListCreateAPIView.as_view(), name='datasource-list'),
    path('datasources/<uuid:pk>/', DataSourceDetailAPIView.as_view(), name='datasource-detail'),

    # KPIs
    path('kpis/', KPIModelListCreateAPIView.as_view(), name='kpimodel-list'),
    path('kpis/<uuid:pk>/', KPIModelDetailAPIView.as_view(), name='kpimodel-detail'),
]
