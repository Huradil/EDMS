from keydev_reports.models import ReportTemplate

from project.users.models import User

from .models import Document

def create_document(
    name: str,
    created_user: User,
    responsible_users: list[User],
    description: str = None,
    file: bytes = None,
    document_template: ReportTemplate = None,
) -> Document:
    doc = Document.objects.create(
        name=name,
        created_by=created_user,
        description=description,
        file=file,
        document_template=document_template,
    )
    doc.responsible_users.set(responsible_users)
    return doc


