


from django import forms
from .models import Task

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from .models import Task

class CompletionReportForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['completion_report', 'worked_hours']
        widgets = {
            'completion_report': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4
            }),
            'worked_hours': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'step': 0.1
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.label_class = 'form-label'
        self.helper.field_class = 'form-control'
        self.helper.layout = Layout(
            'completion_report',
            'worked_hours',
        )
