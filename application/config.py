import os

class Config:
    
    DEBUG = True 
    PORT = 5009
    DATABASE = 'users.db' 
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_super_secret_key_please_change_this_for_prod')
    BCRYPT_LOG_ROUNDS = 12