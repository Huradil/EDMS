from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib import messages

from project.users.models import User
from project.users.forms import UserCreateForm
from project.users.functions import create_user


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None=None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class UserCreateView(View):
    sidebar_group = 'Пользователи'
    sidebar_name = 'Создать пользователя'
    sidebar_icon = 'fas fa-user-plus'
    form_class = UserCreateForm
    template_name = 'users/user_create.html'

    def get(self, request):
        return render(request, self.template_name, context={
            'form': self.form_class()
        })

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                user = create_user(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data.get('email', None),
                    patronymic=form.cleaned_data.get('patronymic', None)
                )
            except Exception as e:
                messages.error(request,_(f'Error {e}'))
            else:
                messages.success(request, _('User was successfully created'))
                return redirect(reverse('users:detail', kwargs={'username': user.username}))
        else:
            messages.error(request, _(f'Error in form {form.errors}'))






