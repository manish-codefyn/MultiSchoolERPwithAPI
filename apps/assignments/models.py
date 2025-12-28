from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

class Assignment(BaseModel):
    """
    Assignments, Homework, and Projects created by teachers
    """
    ASSIGNMENT_TYPE_CHOICES = (
        ("HOMEWORK", _("Homework")),
        ("CLASSWORK", _("Classwork")),
        ("PROJECT", _("Project")),
        ("WORKSHEET", _("Worksheet")),
        ("ASSESSMENT", _("Assessment")),
        ("LAB_REPORT", _("Lab Report")),
        ("OTHER", _("Other")),
    )

    STATUS_CHOICES = (
        ("DRAFT", _("Draft")),
        ("PUBLISHED", _("Published")),
        ("ARCHIVED", _("Archived")),
    )
    
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    assignment_type = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_TYPE_CHOICES,
        default="HOMEWORK",
        verbose_name=_("Assignment Type")
    )
    
    # Class Context
    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Academic Year")
    )
    class_name = models.ForeignKey(
        "academics.SchoolClass",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Class")
    )
    section = models.ForeignKey(
        "academics.Section",
        on_delete=models.CASCADE,
        related_name="assignments",
        null=True,
        blank=True,
        verbose_name=_("Section"),
        help_text=_("Optional. If empty, applies to all sections of the class.")
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("Subject")
    )
    
    # Dates
    assigned_date = models.DateField(default=timezone.localdate, verbose_name=_("Assigned Date"))
    due_date = models.DateTimeField(verbose_name=_("Due Date"))
    
    # Grading
    max_marks = models.PositiveIntegerField(
        default=10, 
        verbose_name=_("Maximum Marks"),
        help_text=_("Maximum marks achievable")
    )
    
    # Resources
    attachment = models.FileField(
        upload_to='assignments/resources/',
        null=True,
        blank=True,
        verbose_name=_("Attachment")
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PUBLISHED",
        verbose_name=_("Status")
    )
    
    # Teacher
    created_by_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assignments",
        verbose_name=_("Created By (Teacher)")
    )

    class Meta:
        db_table = "assignments_assignment"
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")
        ordering = ["-assigned_date", "-created_at"]
        indexes = [
            models.Index(fields=['class_name', 'subject']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.class_name})"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date


class Submission(BaseModel):
    """
    Student submissions for assignments
    """
    STATUS_CHOICES = (
        ("SUBMITTED", _("Submitted")),
        ("LATE", _("Late Submission")),
        ("GRADED", _("Graded")),
        ("RETURNED", _("Returned for Revision")),
        ("RESUBMITTED", _("Resubmitted")),
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name=_("Assignment")
    )
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
        verbose_name=_("Student")
    )
    
    # Submission Content
    submission_text = models.TextField(blank=True, verbose_name=_("Submission Text"))
    submission_file = models.FileField(
        upload_to='assignments/submissions/',
        null=True,
        blank=True,
        verbose_name=_("Submission File")
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Submitted At"))
    
    # Grading
    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Marks Obtained")
    )
    teacher_remarks = models.TextField(blank=True, verbose_name=_("Teacher Remarks"))
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SUBMITTED",
        verbose_name=_("Status")
    )
    
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
        verbose_name=_("Graded By")
    )
    graded_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Graded At"))

    class Meta:
        db_table = "assignments_submission"
        verbose_name = _("Submission")
        verbose_name_plural = _("Submissions")
        unique_together = [['assignment', 'student']]
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student} - {self.assignment.title}"

    def clean(self):
        if self.marks_obtained is not None and self.marks_obtained > self.assignment.max_marks:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'marks_obtained': _(f"Marks cannot exceed maximum marks ({self.assignment.max_marks})")
            })

    def save(self, *args, **kwargs):
        # Auto-mark as late if submitted after due date
        if not self.pk:  # Only on creation
            if timezone.now() > self.assignment.due_date:
                self.status = "LATE"
        
        super().save(*args, **kwargs)