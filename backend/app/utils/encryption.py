import os, base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from flask import current_app

def _get_key():
    key = current_app.config["AES_KEY"]
    if isinstance(key, str):
        key = key.encode()
    return key[:32].ljust(32, b"0")

def encrypt_field(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    key = _get_key()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    enc = cipher.encryptor()
    ct = enc.update(plaintext.encode()) + enc.finalize()
    return base64.b64encode(iv + ct).decode()

def decrypt_field(ciphertext) -> str:
    if not ciphertext:
        return ""
    try:
        key = _get_key()
        if isinstance(ciphertext, str):
            ciphertext = ciphertext.encode("utf-8")
        raw = base64.b64decode(ciphertext)
        iv, ct = raw[:16], raw[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        dec = cipher.decryptor()
        return (dec.update(ct) + dec.finalize()).decode()
    except Exception:
        return "[ENCRYPTED]"
