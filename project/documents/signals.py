import logging
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from project.documents.models import Document
from project.documents.functions import notify_users_about_document
from project.users.models import User


# @receiver(post_save, sender=Document)
# def create_push_notification_for_responsible_users(
#     sender, instance, created, **kwargs
# ) -> None:
#     if created:
#         notify_users_about_document(instance)

@receiver(m2m_changed, sender=Document.responsible_users.through)
def create_push_notification_responsible_users(
    sender, instance, action, pk_set, **kwargs
) -> None:
    if action == 'post_add':
        for pk in pk_set:
            user = User.objects.filter(pk=pk).first()
            if user is None:
                raise Exception(f'Responsible user of document with id {pk} not found!')
            notify_users_about_document(user, instance)

