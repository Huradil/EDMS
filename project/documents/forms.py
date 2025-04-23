from django import forms
from django_select2 import forms as select2

from project.documents.models import Document


class MultipleUserWidget(select2.ModelSelect2MultipleWidget):
    search_fields = ['username__icontains', 'fullname__icontains']


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file', 'responsible_users', 'description']
        widgets = {
            'responsible_users': MultipleUserWidget,
        }
