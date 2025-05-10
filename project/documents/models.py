import base64
from django.db import models

from project.users.models import User
from keydev_reports.models import ReportTemplate

def document_template_directory_path(instance, filename):
    return f'documents/templates/{instance.id}/{filename}'

def document_directory_path(instance, filename):
    return f'documents/requests/{instance.created_by.username}/{filename}'

# class DocumentTemplate(models.Model):
#     name = models.CharField(max_length=255, verbose_name='Название шаблона', help_text='Укажите название шаблона')
#     file = models.FileField(upload_to=document_template_directory_path, verbose_name='Файл шаблона',
#                             help_text='Загрузите файл шаблона')
#     model_name = models.CharField(max_length=255, verbose_name='Название модели', default='Position',
#                                   help_text='Укажите название модели')
#
#     def __str__(self):
#         return self.name


class Document(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название', help_text='Укажите название документа')
    file = models.FileField(upload_to=document_directory_path, verbose_name='Файл',
                            help_text='Загрузите файл', null=True, blank=True)
    document_template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, verbose_name='Шаблон',
                                          related_name='documents', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создал', related_name='documents')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    responsible_users = models.ManyToManyField(User, verbose_name='Ответственные', related_name='responsible_documents')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    def __str__(self):
        return self.name

    def verify_signature(self, signature: str, user: User) -> bool:
        signature_bytes = base64.b64decode(signature)
        with open(self.file.path, 'rb') as f:
            document_bytes = f.read()
        return user.verify_signature(document_bytes, signature_bytes)


class Signature(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name='Документ', related_name='signatures')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='signatures')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    signature = models.TextField(verbose_name='Подпись')

    def __str__(self):
        return f'{self.user.username} - {self.document.name}'


class ChatMessage(models.Model):
    user = models.ForeignKey(User, verbose_name='Отправитель', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255, verbose_name='Комната сообщения')
    text = models.TextField(verbose_name='Текст сообщения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сообщения')

    def __str__(self):
        return f'{self.user.username} - {self.room_name}'
