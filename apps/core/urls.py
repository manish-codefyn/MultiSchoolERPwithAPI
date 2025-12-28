from django.urls import path
from apps.core import views

app_name = 'core'

urlpatterns = [
    path('search/', views.GlobalSearchView.as_view(), name='global_search'),
]
