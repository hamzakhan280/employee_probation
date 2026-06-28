import json
import shutil
import tempfile
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Department, Employee, EmployeeDocument, ProbationApproval


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class EmployeeViewRegressionTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='password123',
        )
        self.client.force_login(self.user)
        self.department = Department.objects.create(
            name='Engineering',
            email='engineering@example.com',
        )
        self.employee = Employee.objects.create(
            employee_id='EMP-001',
            name='Alice Example',
            designation='Engineer',
            department=self.department,
            start_date=date.today() - relativedelta(months=5),
        )

    def test_employee_documents_route_accepts_employee_id_strings(self):
        response = self.client.get(reverse('employee_documents', args=[self.employee.employee_id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['employee'], self.employee)

    def test_document_upload_ajax_accepts_employee_identifier(self):
        response = self.client.post(
            reverse('upload_document_ajax'),
            data={
                'employee_id': self.employee.employee_id,
                'title': 'Offer',
                'document_type': 'pdf',
                'description': 'Offer letter',
                'file': SimpleUploadedFile('offer.pdf', b'pdf-bytes', content_type='application/pdf'),
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertEqual(EmployeeDocument.objects.get().employee, self.employee)

    def test_employee_list_search_supports_department_name(self):
        response = self.client.get(reverse('employee_list'), {'q': 'Engineering'})

        self.assertEqual(response.status_code, 200)
        page_items = list(response.context['page_obj'].object_list)
        self.assertIn(self.employee, page_items)

    def test_generate_document_api_supports_json_payload(self):
        response = self.client.post(
            reverse('generate_document'),
            data=json.dumps({
                'document_type': 'service_certificate',
                'employee_data': {
                    'name': self.employee.name,
                    'employee_id': self.employee.employee_id,
                    'designation': self.employee.designation,
                    'department': self.department.name,
                    'start_date': str(self.employee.start_date),
                },
                'additional_info': 'Include strong performance.',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertIn('service certificate', payload['document'].lower())

    def test_probation_extension_persists_extended_end_date(self):
        response = self.client.post(
            reverse('probation_approval_ajax', args=[self.employee.employee_id]),
            data={'action': 'extend', 'extension_months': '2', 'comments': 'Needs more time'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])

        self.employee.refresh_from_db()
        approval = ProbationApproval.objects.get(employee=self.employee)
        self.assertTrue(self.employee.is_extended)
        self.assertEqual(self.employee.probation_status, 'Extended')
        self.assertEqual(self.employee.extended_probation_end_date, approval.extended_end_date)
