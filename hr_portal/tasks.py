from celery import shared_task
from django.core.management import call_command
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import date, timedelta

@shared_task
def check_probation_expirations():
    """Celery task to check probation expirations and send notifications"""
    call_command('send_probation_notifications')


@shared_task
def send_probation_notifications_task():
    """
    Celery task to send automatic email notifications for employees with less than 15 days remaining in probation
    """
    from hr_portal.models import Employee, ProbationNotification

    # Find employees with less than 15 days remaining in probation
    future_date = date.today() + timedelta(days=15)
    employees = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon']
    )

    results = []
    for employee in employees:
        # Check if a notification has already been sent for this employee today
        if not ProbationNotification.objects.filter(
            employee=employee,
            notification_date__date=date.today(),
            notification_type='automatic_email'
        ).exists():

            # Calculate probation progress percentage
            total_probation_days = 180  # Assuming 6 months probation (approx.)
            days_completed = total_probation_days - employee.days_until_probation_end
            progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

            # Prepare context for the email template
            context = {
                'employee_name': employee.name,
                'employee_id': employee.employee_id,
                'employee_designation': employee.designation,
                'employee_department': employee.department,
                'employee_start_date': employee.start_date.strftime('%B %d, %Y'),
                'employee_end_date': employee.end_date.strftime('%B %d, %Y'),
                'days_until_probation_end': employee.days_until_probation_end,
                'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
                'progress_percentage': progress_percentage,
            }

            # Render the HTML email template
            html_message = render_to_string('hr_portal/enhanced_probation_notification_email.html', context)

            # Determine recipient email - default to muhammad.hamza@giki.edu.pk
            recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')

            # If department has an email, use that instead
            if (employee.department and
                hasattr(employee.department, 'email') and
                employee.department.email):
                recipient_email = employee.department.email
            else:
                # Use the default HR email from settings
                recipient_email = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')

            # List of additional HR members to CC
            hr_cc_emails = [
                'hikmatullah@giki.edu.pk',
                'nasirali@giki.edu.pk',
                'saboor@giki.edu.pk',
                'israr.hassan@giki.edu.pk',
                'shahid@giki.edu.pk'
            ]

            # Add the main HR contact to CC list
            main_hr = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
            if main_hr not in hr_cc_emails:
                hr_cc_emails.insert(0, main_hr)

            # Create and send the email with CC to HR
            subject = f"Automatic Alert: Probation Period Ending Soon for {employee.name} ({employee.employee_id})"

            email = EmailMultiAlternatives(
                subject=subject,
                body=f"This is an HTML email notification about {employee.name}'s probation period. Please view it in a compatible email client.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],  # Primary recipient is the department
                cc=hr_cc_emails  # CC to main HR and additional HR members
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            # Create a notification record
            ProbationNotification.objects.create(
                employee=employee,
                days_before_expiry=employee.days_until_probation_end,
                sent=True,
                notification_type='automatic_email'
            )

            results.append(f'Successfully sent automatic notification for {employee.name}')
        else:
            results.append(f'Notification already sent today for {employee.name}')

    if not employees:
        results.append('No employees found with less than 15 days remaining in probation')

    return results


@shared_task
def send_weekly_employees_report():
    """
    Celery task to send a weekly report of employees with ending probation to all HR members
    Runs every Tuesday as configured in settings
    """
    from hr_portal.models import Employee

    # Find employees with less than 30 days remaining in probation
    future_date = date.today() + timedelta(days=30)
    employees_queryset = Employee.objects.filter(
        end_date__range=[date.today(), future_date],
        probation_status__in=['Active', 'Ending Soon']
    ).order_by('end_date')

    # Prepare employee data with additional computed fields for the template
    employees = []
    for emp in employees_queryset:
        # Calculate probation progress percentage
        total_probation_days = 180  # Assuming 6 months probation (approx.)
        days_completed = total_probation_days - emp.days_until_probation_end
        progress_percentage = int((days_completed / total_probation_days) * 100) if total_probation_days > 0 else 0

        # Create a dict with all the properties needed for the template
        emp_data = {
            'id': emp.employee_id,
            'name': emp.name,
            'designation': emp.designation,
            'department': emp.department,
            'start_date': emp.start_date.strftime('%B %d, %Y'),
            'end_date': emp.end_date.strftime('%B %d, %Y'),
            'days_until_probation_end': emp.days_until_probation_end,
            'probation_completion_percent': emp.probation_completion_percent,
        }
        employees.append(emp_data)

    # Prepare context for the email template
    context = {
        'employees': employees,
        'current_date': date.today().strftime('%B %d, %Y'),
        'report_title': 'Weekly Probation Report',
        'hr_contact': getattr(settings, 'HR_EMAIL', 'HR Department'),
    }

    # Render the HTML email template
    html_message = render_to_string('hr_portal/probation_report_email.html', context)

    # List of HR members to send the email to
    hr_emails = [
        'hamzamarwat46@gmail.com',
        'muhammad.hamza@giki.edu.pk',
        'hikmatullah@giki.edu.pk',
        'nasirali@giki.edu.pk',
        'saboor@giki.edu.pk',
        'israr.hassan@giki.edu.pk',
        'shahid@giki.edu.pk'
    ]

    # Add the main HR contact if it's not already in the list
    main_hr = getattr(settings, 'HR_EMAIL', 'muhammad.hamza@giki.edu.pk')
    if main_hr not in hr_emails:
        hr_emails.insert(0, main_hr)

    # Create and send the email to all HR members
    subject = f"Weekly Probation Report: {len(employees)} Employees with Ending Probation ({date.today().strftime('%B %d, %Y')})"

    email = EmailMultiAlternatives(
        subject=subject,
        body=f"This is an HTML email report containing a list of employees whose probation periods are ending soon. Please view it in a compatible email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=hr_emails  # Send to all HR members
    )
    email.attach_alternative(html_message, "text/html")
    email.send()

    results = [f'Weekly probation report sent successfully to {len(hr_emails)} HR members. Report contains {len(employees)} employees.']

    if not employees:
        results.append('No employees found with less than 30 days remaining in probation')

    return results


@shared_task
def send_weekly_probation_report_task():
    """Celery task to send weekly probation report via management command"""
    from django.core.management import call_command
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Call the management command to send the weekly probation report
        call_command('send_weekly_probation_report', verbosity=0)
        logger.info("Weekly probation report task completed successfully")
        return "Weekly probation report task completed successfully"
    except Exception as e:
        error_msg = f"Error in weekly probation report task: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg