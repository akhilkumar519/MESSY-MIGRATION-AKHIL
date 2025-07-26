
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from application import config

def hash_password(password):
   
    if not password:
        return None
    try:
       
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        
    except Exception as e:
        
        print(f"Error hashing password: {e}")
        return None

def check_password(password, hashed_password):
    
    if not password or not hashed_password:
        return False
    return check_password_hash(hashed_password, password)