from django import forms
from .models import Employee, Department, EmployeeDocument

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'name', 'designation', 'department', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'employee_id': forms.TextInput(attrs={'placeholder': 'Enter employee ID'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter employee name'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Enter designation'}),
        }

class EmployeeUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select Excel file',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['title', 'document_type', 'file', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter document title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter description'}),
        }