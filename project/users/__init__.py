import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from .cython_generate_keys import generate_keys, decrypt_private_key, sign_document, verify_signature
except ImportError as e:
    print(f"Ошибка импорта cython_generate_keys: {e}")
