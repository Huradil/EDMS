from django.shortcuts import render, redirect, reverse
from django.views.generic import CreateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from project.users.models import User

from .forms import DocumentForm
from .functions import create_document, document_user_sign
from .models import Document, Signature


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


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/document_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        can_sign = False
        sign_users = []
        if user in self.object.responsible_users.all():
            can_sign = True
        for user in self.object.responsible_users.all():
            signature = Signature.objects.filter(document=self.object, user=user).first()
            try:
                sign = self.object.verify_signature(signature.signature, user) if signature else False
            except Exception as e:
                sign = False
            sign_users.append(
                {
                    'fullname': user.fullname,
                    'position': user.employee.position.name if user.employee else None,
                    'sign': sign,
                    'sign_date': signature.created_at if signature and sign else None,
                }
            )

        context['can_sign'] = can_sign
        context['document'] = self.object
        context['responsible_users'] = sign_users
        return context


class DocumentSignView(LoginRequiredMixin, View):
    def post(self, request, pk):
        assert isinstance(request.user, User)
        try:
            result = document_user_sign(
                document_id=pk,
                user_id=request.user.id,
                password=request.POST.get('password'),
            )
        except Exception as e:
            messages.error(request, f'Ошибка при подписании документа: {e}')
        else:
            if result:
                messages.success(request, 'Документ успешно подписан')
            else:
                messages.error(request, 'Неверный пароль для подписи документа')
        return redirect(reverse('documents:document_detail', args=[pk]))




