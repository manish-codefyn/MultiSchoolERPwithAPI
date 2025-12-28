from django.contrib import admin
from .models import Assignment, Submission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'subject', 
        'class_name', 
        'section', 
        'due_date', 
        'assignment_type', 
        'status',
        'is_overdue'
    )
    list_filter = (
        'academic_year', 
        'status', 
        'assignment_type', 
        'class_name', 
        'subject', 
        'due_date'
    )
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    list_per_page = 20

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'assignment', 
        'student', 
        'status', 
        'submitted_at', 
        'marks_obtained'
    )
    list_filter = ('status', 'submitted_at', 'graded_at')
    search_fields = (
        'student__student_profile__admission_number', 
        'assignment__title'
    )
    date_hierarchy = 'submitted_at'
    list_per_page = 20
