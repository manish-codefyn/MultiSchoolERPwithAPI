from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from apps.core.views import BaseListView, BaseCreateView, BaseUpdateView, BaseDetailView, BaseDeleteView
from apps.core.utils.tenant import get_current_tenant
from apps.core.services.notification_service import NotificationService
from apps.students.models import Student
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm

class AssignmentListView(BaseListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    permission_required = 'assignments.view_assignment'

    def get_queryset(self):
        tenant = get_current_tenant()
        queryset = super().get_queryset().filter(tenant=tenant)
        
        # Filter by role
        user = self.request.user
        if user.role == 'student':
            student = user.student_profile
            # Show assignments for student's class and subject
            if student and student.current_class:
                queryset = queryset.filter(
                    class_name=student.current_class
                ).filter(
                    Q(section__isnull=True) | Q(section=student.section)
                )
        elif user.role == 'teacher':
            # Teachers see assignments they created or for their subjects
            queryset = queryset.filter(created_by_teacher=user)

        return queryset.select_related('class_name', 'subject', 'created_by_teacher')

class AssignmentCreateView(BaseCreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    permission_required = 'assignments.add_assignment'
    success_url = reverse_lazy('assignments:assignment_list')

    def form_valid(self, form):
        form.instance.created_by_teacher = self.request.user
        response = super().form_valid(form)
        assignment = self.object
        
        # Send notifications to students
        try:
            students = Student.objects.filter(
                current_class=assignment.class_name,
                is_active=True
            )
            if assignment.section:
                students = students.filter(section=assignment.section)
            
            count = 0
            for student in students:
                if student.user:
                    NotificationService.send_in_app_notification(
                        recipient=student.user,
                        title=f"New Assignment: {assignment.title}",
                        message=f"A new {assignment.get_assignment_type_display().lower()} has been assigned in {assignment.subject.name}. Due: {assignment.due_date.strftime('%d %b %Y')}",
                        notification_type="ACADEMIC",
                        sender=self.request.user,
                        action_url=reverse_lazy('assignments:assignment_detail', kwargs={'pk': assignment.pk}),
                        action_text="View Assignment",
                        tenant=get_current_tenant() # Assuming utility available or use self.request.tenant if middleware sets it
                    )
                    count += 1
            
            if count > 0:
                messages.info(self.request, f"Notification sent to {count} students.")
                
        except Exception as e:
            # Log error but don't fail the creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send assignment notifications: {str(e)}")
            
        messages.success(self.request, "Assignment created successfully.")
        return response

class AssignmentUpdateView(BaseUpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    permission_required = 'assignments.change_assignment'
    success_url = reverse_lazy('assignments:assignment_list')

    def form_valid(self, form):
        messages.success(self.request, "Assignment updated successfully.")
        return super().form_valid(form)

class AssignmentDetailView(BaseDetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    context_object_name = 'assignment'
    permission_required = 'assignments.view_assignment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == 'student':
            # Check if submitted
            context['submission'] = Submission.objects.filter(
                assignment=self.object,
                student=self.request.user.student_profile
            ).first()
            context['submission_form'] = SubmissionForm()
        else:
            context['submissions'] = self.object.submissions.all().select_related('student')
        return context

class AssignmentDeleteView(BaseDeleteView):
    model = Assignment
    template_name = 'assignments/assignment_confirm_delete.html'
    permission_required = 'assignments.delete_assignment'
    success_url = reverse_lazy('assignments:assignment_list')

# Submission Views
class SubmissionCreateView(BaseCreateView):
    model = Submission
    form_class = SubmissionForm
    template_name = 'assignments/submission_form.html'
    permission_required = 'assignments.add_submission'

    def form_valid(self, form):
        assignment = Assignment.objects.get(pk=self.kwargs['assignment_id'])
        form.instance.assignment = assignment
        form.instance.student = self.request.user.student_profile
        messages.success(self.request, "Assignment submitted successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('assignments:assignment_detail', kwargs={'pk': self.kwargs['assignment_id']})
