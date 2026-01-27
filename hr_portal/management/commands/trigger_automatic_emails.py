from django.core.management.base import BaseCommand
from hr_portal.tasks import send_probation_notifications_task, send_weekly_employees_report
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Trigger automatic email notifications for probation expirations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['daily', 'weekly'],
            default='daily',
            help='Type of email notifications to send (daily or weekly)'
        )

    def handle(self, *args, **options):
        email_type = options['type']
        
        if email_type == 'daily':
            self.stdout.write(
                self.style.WARNING('Sending daily probation notifications...')
            )
            result = send_probation_notifications_task.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Daily probation notifications task queued with ID: {result.id}')
            )
        elif email_type == 'weekly':
            self.stdout.write(
                self.style.WARNING('Sending weekly probation report...')
            )
            result = send_weekly_employees_report.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Weekly probation report task queued with ID: {result.id}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Email notification tasks completed successfully')
        )