from django import forms
from django.contrib.auth.mixins import PermissionRequiredMixin


class FormControlMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                field.widget.attrs['class'] = 'form-control datepicker-input'
                field.widget.attrs['onfocus'] = 'toggleDatePicker(this)'
            elif isinstance(field, forms.DateTimeField):
                field.widget.attrs['class'] = 'form-control datetimepicker-input'
                field.widget.attrs['onfocus'] = 'toggleDatePicker(this)'
            elif isinstance(field, forms.FileField):
                field.widget.attrs['class'] = 'custom-file-input'
            elif isinstance(field, forms.ModelMultipleChoiceField):
                field.widget.attrs['class'] = 'form-control selectpicker'
                field.widget.attrs['title'] = field.label
            else:
                field.widget.attrs['class'] = 'form-control'


class BasePermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        return self.has_perms(perms)

    def has_perm(self, perm, obj=None):
        return self.request.user.has_permission_user(perm)

    def has_perms(self, perm_list, obj=None):
        return all(self.has_perm(perm, obj) for perm in perm_list)
