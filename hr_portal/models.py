from django.db import models
from datetime import timedelta
import os
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

def employee_document_upload_path(instance, filename):
    """Generate upload path for employee documents"""
    return f'employees/{instance.employee.employee_id}/{filename}'

def template_upload_path(instance, filename):
    """Generate upload path for document templates"""
    return f'templates/{filename}'

class Department(models.Model):
    """Model to store department information including email addresses"""
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(help_text="Email address for department head")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    STATUS_ACTIVE = 'Active'
    STATUS_ENDING_SOON = 'Ending Soon'
    STATUS_COMPLETED = 'Completed'
    STATUS_EXTENDED = 'Extended'
    STATUS_REJECTED = 'Rejected'

    employee_id = models.CharField(max_length=20, unique=True, verbose_name="S.#")
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(editable=False)
    probation_status = models.CharField(max_length=20, default=STATUS_ACTIVE)
    extended_probation_end_date = models.DateField(null=True, blank=True, help_text="New end date if probation is extended")
    is_extended = models.BooleanField(default=False, help_text="Indicates if the probation period has been extended")

    def save(self, *args, **kwargs):
        # Automatically calculate end date as 6 months from start date using relativedelta for accuracy
        from datetime import date
        self.end_date = self.start_date + relativedelta(months=6)

        # Use extended end date if probation has been extended
        current_end_date = self.current_end_date

        # Update probation status based on current date
        if self.probation_status not in {self.STATUS_REJECTED, self.STATUS_COMPLETED}:
            if self.is_extended and current_end_date >= date.today():
                self.probation_status = self.STATUS_EXTENDED
            elif current_end_date < date.today():
                self.probation_status = self.STATUS_COMPLETED
            elif self.is_probation_ending_soon:
                self.probation_status = self.STATUS_ENDING_SOON
            else:
                self.probation_status = self.STATUS_ACTIVE

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    @property
    def days_until_probation_end(self):
        """Calculate days remaining until probation ends"""
        from datetime import date
        # Use extended end date if probation has been extended
        current_end_date = self.extended_probation_end_date if self.is_extended else self.end_date
        return (current_end_date - date.today()).days

    @property
    def is_probation_ending_soon(self):
        """Check if probation ends within 30 days (1 month)"""
        from datetime import date
        # Use extended end date if probation has been extended
        current_end_date = self.extended_probation_end_date if self.is_extended else self.end_date
        days_remaining = (current_end_date - date.today()).days
        return days_remaining <= 30 and days_remaining >= 0

    @property
    def current_end_date(self):
        """Return the current end date (original or extended)"""
        return self.extended_probation_end_date if self.is_extended and self.extended_probation_end_date else self.end_date

    @property
    def probation_completion_percent(self):
        """Calculate the percentage of probation completed (0-100%)"""
        from datetime import date
        # Base the percentage on the actual probation window, including extensions.
        total_probation_days = max((self.current_end_date - self.start_date).days, 1)
        days_completed = total_probation_days - self.days_until_probation_end
        percent = (days_completed / total_probation_days) * 100 if total_probation_days > 0 else 0
        return min(100, max(0, round(percent)))  # Clamp between 0 and 100

class DocumentTemplate(models.Model):
    """Template for generating documents"""
    DOCUMENT_TYPES = [
        ('probation_letter', 'Probation Letter'),
        ('service_certificate', 'Service Certificate'),
        ('experience_certificate', 'Experience Certificate'),
        ('probation_note', 'Probation Note'),
        ('offer_letter', 'Offer Letter'),
        ('appointment_letter', 'Appointment Letter'),
        ('termination_letter', 'Termination Letter'),
        ('transfer_letter', 'Transfer Letter'),
        ('promotion_letter', 'Promotion Letter'),
        ('salary_increment_letter', 'Salary Increment Letter'),
        ('probation_extension_letter', 'Probation Extension Letter'),
        ('probation_confirmation_letter', 'Probation Confirmation Letter'),
        ('probation_draft', 'Probation Draft'),
        ('probation_evaluation_form', 'Probation Evaluation Form'),
        ('warning_letter', 'Warning Letter'),
        ('resignation_acceptance_letter', 'Resignation Acceptance Letter'),
        ('resignation_draft', 'Resignation Draft'),

        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=35, choices=DOCUMENT_TYPES)
    template_file = models.FileField(upload_to=template_upload_path)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ('excel', 'Excel'),
        ('word', 'Word'),
        ('pdf', 'PDF'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=employee_document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.employee.name}"

class GeneratedDocument(models.Model):
    """Generated documents based on templates"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='generated_documents')
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE)
    document_file = models.FileField(upload_to=employee_document_upload_path)
    generated_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.employee.name}"

class ProbationApproval(models.Model):
    """Track probation approval process"""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    EXTENDED = 'extended'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (EXTENDED, 'Extended'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    requested_by = models.CharField(max_length=100, blank=True)  # HR staff who initiated
    approved_by = models.CharField(max_length=100, blank=True)  # Department head who approved
    approval_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extension_months = models.IntegerField(default=0, help_text="Number of months to extend probation")
    extended_end_date = models.DateField(null=True, blank=True, help_text="New end date after extension")

    def __str__(self):
        return f"{self.employee.name} - {self.get_approval_status_display()}"

class ProbationNotification(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    notification_date = models.DateTimeField(auto_now_add=True)
    days_before_expiry = models.IntegerField()
    sent = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, default='probation_reminder')  # probation_reminder, approval_request, etc.

    def __str__(self):
        return f"Notification for {self.employee.name} - {self.days_before_expiry} days before expiry"