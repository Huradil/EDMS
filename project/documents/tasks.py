from typing import Iterable
import logging

from pathlib import Path
from django.conf import settings
from celery import shared_task
from project.documents.models import ChatMessage
from project.users.models import User
from datetime import datetime
from keydev_reports.exporter import TemplateReportExporter
from project.documents.models import Document


@shared_task
def save_message_task(user_id: int, text: str, room_name: str, created_at: datetime ):
    user = User.objects.filter(id=user_id).first()
    if user is None:
        return None
    ChatMessage.objects.create(
        user=user,
        room_name=room_name,
        text=text,
        created_at=created_at
    )


@shared_task
def get_template_report(
    report_data: Iterable,
    user_name: str,
    report_id: int,
    provider_name: str,
    document_id: int,
    file_name: str | None = None
):
    report = TemplateReportExporter(
        report_data=report_data,
        user_name=user_name,
        report_id=report_id,
        provider_name=provider_name,
        file_name=file_name
    )
    data = dict()
    try:
        file = report.get_report()
    except Exception as e:
        data['error'] = str(e)
    else:
        document = Document.objects.filter(id=document_id).first()
        if document is None:
            data['error'] = 'Document objects was not found!'
        full_path = Path(file)
        relative_path = full_path.relative_to(settings.MEDIA_ROOT)
        document.file.name = str(relative_path)
        document.save()
        data['file'] = file
    return data


