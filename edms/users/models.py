import base64, os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


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
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Шифруем закрытый ключ
        salt = os.urandom(16)  # Соль для безопасности
        key = PBKDF2HMAC(algorithm=algorithms.AES, length=32, salt=salt, iterations=100000).derive(password.encode())

        cipher = Cipher(algorithms.AES(key), modes.CFB(salt))
        encryptor = cipher.encryptor()
        encrypted_key = encryptor.update(private_pem) + encryptor.finalize()


        # Откртый ключ
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self.private_key = base64.b16encode(salt + encrypted_key).decode("utf-8")
        self.public_key = public_pem.decode("utf-8")

    def save(self, *args, **kwargs):
        if not self.private_key or not self.public_key:
            self.generate_keys()
        if not self.fullname:
            self.fullname = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)

    def _decrypt_private_key(self, password: str):
        encrypted_data = base64.b64decode(self.private_key)
        salt, encrypted_key = encrypted_data[:16], encrypted_data[16:]

        key = PBKDF2HMAC(algorithm=algorithms.AES, length=32, salt=salt, iterations=100000).derive(password.encode())
        cipher = Cipher(algorithms.AES(key), modes.CFB(salt))
        decryptor = cipher.decryptor()
        private_pem = decryptor.update(encrypted_key) + decryptor.finalize()

        return private_pem

    def sign_document(self, document: bytes, password: str) -> bytes:
        private_pem = self._decrypt_private_key(password)
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=None,
        )
        signature = private_key.sign(
            document,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return signature

    def verify_signature(self, document: bytes, signature: bytes) -> bool:
        public_key = serialization.load_pem_public_key(self.public_key.encode())
        try:
            public_key.verify(
                signature,
                document,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False



    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
