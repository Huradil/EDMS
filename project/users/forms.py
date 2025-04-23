from cProfile import label

from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django import forms
from django_select2 import forms as s2_forms

from project.contrib.mixins import FormControlMixin
from .models import User, Department, Position, UserEmployee


class DepartmentWidget(s2_forms.ModelSelect2Widget):
    search_fields = ['name__icontains', 'parent__name__icontains', 'branch__name__icontains']


class PositionWidget(s2_forms.ModelSelect2Widget):
    search_fields = ['name__icontains', 'department__name__icontains']


class UserWidget(s2_forms.ModelSelect2Widget):
    search_fields = ['username__icontains', 'first_name__icontains', 'last_name__icontains', 'patronymic__icontains']


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput, validators=[validate_password, ])
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'username', 'email', 'password1', 'password2']

    def clean(self):
        super(UserCreateForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self._errors['password1'] = self.error_class(['Пароли не совпадают!'])
        return self.cleaned_data


class UserKeyPasswordForm(forms.Form):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)

    def clean(self):
        super(UserKeyPasswordForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self._errors['password1'] = self.error_class(['Пароли не совпадают!'])
        return self.cleaned_data


class DepartmentForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'parent', 'branch', 'description']
        widgets = {
            'parent': DepartmentWidget,
        }


class PositionForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'department', 'description']
        widgets = {
            'department': DepartmentWidget,
        }


class UserEmployeeForm(FormControlMixin, forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = UserEmployee
        fields = ['user', 'position','start_date']
        widgets = {
            'user': UserWidget,
            'position': PositionWidget,
        }


