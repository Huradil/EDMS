import base64
from keydev_reports.models import ReportTemplate

from project.users.models import User

from .models import Document, Signature

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


def document_user_sign(document_id: int, user_id: int, password: str):
    document = Document.objects.filter(id=document_id).first()
    if document is None:
        raise Exception("Document not found")
    user = User.objects.filter(id=user_id).first()
    if user is None:
        raise Exception("User not found")
    if document.file is None:
        raise Exception("Document file not found")
    with document.file.open('rb') as f:
        file_bytes = f.read()
    signature = user.sign_document(file_bytes, password)
    result = user.verify_signature(file_bytes, signature)
    if result:
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        Signature.objects.create(
            document=document,
            user=user,
            signature=signature_b64,
        )
        return True
    return False




