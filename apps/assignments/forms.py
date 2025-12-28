from django import forms
from apps.core.forms import TenantAwareModelForm
from .models import Assignment, Submission

class AssignmentForm(TenantAwareModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'assignment_type', 'academic_year', 'class_name', 'section', 'subject', 'due_date', 'max_marks', 'attachment', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SubmissionForm(TenantAwareModelForm):
    class Meta:
        model = Submission
        fields = ['submission_text', 'submission_file']
        widgets = {
            'submission_text': forms.Textarea(attrs={'rows': 4}),
        }
