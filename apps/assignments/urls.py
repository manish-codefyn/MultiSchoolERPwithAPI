from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', login_required(views.AssignmentListView.as_view()), name='assignment_list'),
    path('create/', login_required(views.AssignmentCreateView.as_view()), name='assignment_create'),
    path('<uuid:pk>/', include([
        path('', login_required(views.AssignmentDetailView.as_view()), name='assignment_detail'),
        path('edit/', login_required(views.AssignmentUpdateView.as_view()), name='assignment_update'),
        path('delete/', login_required(views.AssignmentDeleteView.as_view()), name='assignment_delete'),
        path('submit/', login_required(views.SubmissionCreateView.as_view()), name='submission_create'),
    ])),
]
