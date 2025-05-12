import hashlib

def hash_password(password):
    """Devuelve el hash SHA256 de la contraseña."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, hashed):
    """Verifica si la contraseña coincide con el hash."""
    return hash_password(password) == hashed