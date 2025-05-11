from django import forms
from django_select2 import forms as select2

from project.documents.models import Document


class MultipleUserWidget(select2.ModelSelect2MultipleWidget):
    search_fields = ['username__icontains', 'fullname__icontains']


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file', 'document_template', 'responsible_users', 'description']
        widgets = {
            'responsible_users': MultipleUserWidget,
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        template = cleaned_data.get('document_template')
        if not file and not template:
            raise forms.ValidationError('Укажите один из полей: файл, шаблон!')
        if file and template:
            raise forms.ValidationError('Укажите только один из полей: файл или шаблон!')
