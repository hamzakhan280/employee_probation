from django.core.management.base import BaseCommand
from hr_portal.models import Department

class Command(BaseCommand):
    help = 'Set up default departments with email addresses'

    def handle(self, *args, **options):
        default_departments = [
            {'name': 'Computer Science', 'email': 'hamzamarwat46@gmail.com', 'description': 'Computer Science Department'},
            {'name': 'Electrical Engineering', 'email': 'hamzamarwat46@gmail.com', 'description': 'Electrical Engineering Department'},
            {'name': 'Mechanical Engineering', 'email': 'hamzamarwat46@gmail.com', 'description': 'Mechanical Engineering Department'},
            {'name': 'Mathematics', 'email': 'hamzamarwat46@gmail.com', 'description': 'Mathematics Department'},
            {'name': 'Physics', 'email': 'hamzamarwat46@gmail.com', 'description': 'Physics Department'},
            {'name': 'Chemistry', 'email': 'hamzamarwat46@gmail.com', 'description': 'Chemistry Department'},
            {'name': 'Biology', 'email': 'hamzamarwat46@gmail.com', 'description': 'Biology Department'},
            {'name': 'Business Administration', 'email': 'hamzamarwat46@gmail.com', 'description': 'Business Administration Department'},
            {'name': 'Humanities', 'email': 'hamzamarwat46@gmail.com', 'description': 'Humanities Department'},
            {'name': 'Other', 'email': 'hamzamarwat46@gmail.com', 'description': 'General Department'},
        ]

        created_count = 0
        for dept_data in default_departments:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'email': dept_data['email'],
                    'description': dept_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created department: {dept.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Department already exists: {dept.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Setup complete. {created_count} departments created.')
        )