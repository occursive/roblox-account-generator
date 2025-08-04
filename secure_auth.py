from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from base64 import b64encode
from time import time
from headers import headers3

def get_sa(session):
    try:
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        public_key = private_key.public_key()
        spki_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        client_public_key = b64encode(spki_bytes).decode('utf-8')
        client_epoch_timestamp = str(int(time()))
        response = session.get(url="https://apis.roblox.com/hba-service/v1/getServerNonce", headers=headers3())
        response.raise_for_status()
        server_nonce = response.text.strip('"')

        payload = f"{client_public_key}|{client_epoch_timestamp}|{server_nonce}".encode('utf-8')
        signature = private_key.sign(payload, ec.ECDSA(hashes.SHA256()))
        sai_signature = b64encode(signature).decode('utf-8')

        return client_public_key, client_epoch_timestamp, server_nonce, sai_signature
    except Exception:
            return None, None, None, None
