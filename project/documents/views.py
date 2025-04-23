from django.shortcuts import render, redirect, reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from project.users.models import User

from .forms import DocumentForm
from .functions import create_document


class DocumentCreateView(LoginRequiredMixin,CreateView):
    template_name = 'standard_form.html'
    form_class = DocumentForm
    sidebar_group = 'Документы'
    sidebar_name = 'Запрос документа'
    sidebar_icon = 'fa-solid fa-file-import'

    def get(self, request):
        assert isinstance(request.user, User)
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        assert isinstance(request.user, User)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = create_document(
                    name=form.cleaned_data['name'],
                    created_user=request.user,
                    file=request.FILES['file'],
                    responsible_users=form.cleaned_data.get('responsible_users'),
                    description=form.cleaned_data.get('description'),
                    document_template=form.cleaned_data.get('document_template'),
                )
            except Exception as e:
                messages.error(request, f'Ошибка при создании документа: {e}')
                return self.render_to_response(self.get_context_data(form=form))
            else:
                messages.success(request, f'Документ {document.name} успешно создан')
                return redirect(reverse('documents:document_create'))
        else:
            messages.error(request, 'Ошибка при заполнении формы')
            return self.form_invalid(form)


