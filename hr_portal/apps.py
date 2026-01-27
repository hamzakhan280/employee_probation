from django.apps import AppConfig

class HrPortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_portal'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':  # Prevents running during migrations
            try:
                from django_celery_beat.models import PeriodicTask, IntervalSchedule
                from celery import current_app
                import json

                # Create interval schedule for daily checks
                schedule, created = IntervalSchedule.objects.get_or_create(
                    every=1,
                    period=IntervalSchedule.DAYS,
                )

                # Create periodic task for sending notifications
                PeriodicTask.objects.get_or_create(
                    interval=schedule,
                    name='Daily Probation Notifications Check',
                    task='hr_portal.tasks.check_probation_expirations',
                )
            except RuntimeError:
                # Handle the case where the app isn't fully loaded yet
                pass
            except LookupError:
                # Handle the case where the database tables don't exist yet
                pass