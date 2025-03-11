import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_keys(password: str):
    """Генерация RSA-ключей и шифрование закрытого ключа"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Генерация PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Генерация соли и ключа
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = kdf.derive(password.encode())

    # Генерация случайного IV
    iv = os.urandom(16)

    # AES-CBC шифрование с PKCS7 padding
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Padding PKCS7 (чтобы длина была кратна 16)
    pad_len = 16 - (len(private_pem) % 16)
    private_pem_padded = private_pem + bytes([pad_len]) * pad_len

    encrypted_key = encryptor.update(private_pem_padded) + encryptor.finalize()

    # Возвращаем зашифрованный ключ и публичный ключ
    return (
        base64.b64encode(salt + iv + encrypted_key).decode("utf-8"),
        public_pem.decode("utf-8")
    )

def decrypt_private_key(encrypted_private_key: str, password: str):
    """Дешифрование закрытого ключа"""
    encrypted_data = base64.b64decode(encrypted_private_key)
    salt, iv, encrypted_key = encrypted_data[:16], encrypted_data[16:32], encrypted_data[32:]

    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    private_pem_padded = decryptor.update(encrypted_key) + decryptor.finalize()

    # Убираем padding
    pad_len = private_pem_padded[-1]
    private_pem = private_pem_padded[:-pad_len]

    return private_pem

def sign_document(encrypted_private_key: str, password: str, document: bytes):
    """Подписание документа"""
    private_pem = decrypt_private_key(encrypted_private_key, password)

    private_key = serialization.load_pem_private_key(private_pem, password=None)

    return private_key.sign(
        document,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify_signature(public_key: str, document: bytes, signature: bytes):
    """Проверка подписи"""
    public_key_obj = serialization.load_pem_public_key(public_key.encode())
    try:
        public_key_obj.verify(
            signature,
            document,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
