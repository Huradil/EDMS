import base64, os
from inspect import signature

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cython_generate_keys import generate_keys, decrypt_private_key, sign_document, verify_signature


class User(AbstractUser):
    """
    Default custom user model for Electronic Documents Management.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    fullname = models.CharField(max_length=255, verbose_name="ФИО пользователя", help_text="Введите фио пользователя",
                                null=True, blank=True)
    patronymic = models.CharField(max_length=255, verbose_name="Отчество", help_text="Введите отчество",
                                  null=True, blank=True)
    private_key = models.TextField(blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def generate_keys(self, password: str):
        self.private_key, self.public_key = generate_keys(password)
        self.save()

    def save(self, *args, **kwargs):
        if not self.fullname:
            self.fullname = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)

    def sign_document(self, document: bytes, password: str) -> bytes:
        if self.private_key is None or self.private_key == "":
            raise Exception("Не был найден приватный ключ для подписи")
        signature: bytes = sign_document(self.private_key, password, document)
        return signature

    def verify_signature(self, document: bytes, signature: bytes) -> bool:
        if self.public_key is None or self.private_key == "":
            raise Exception("Не был найден публичный ключ")
        result: bool = verify_signature(self.public_key, document, signature)
        return result


    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
