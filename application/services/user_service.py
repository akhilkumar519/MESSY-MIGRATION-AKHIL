import sqlite3
from application.models.user_model import UserModel
from application.utils.security import hash_password, check_password

class UserService:
    def __init__(self):
        self.user_model = UserModel()

    def get_all_users(self):
        return self.user_model.get_all_users()

    def get_user_by_id(self, user_id):
        return self.user_model.get_user_by_id(user_id)

    def create_user(self, name, email, password):
        if not name or not email or not password:
            return None, "All fields (name, email, password) are required."

        # Check for existing name or email before proceeding
        if self.user_model.get_user_by_name(name):
            return None, "Name already exists" 
        
        if self.user_model.get_user_by_email(email):
            return None, "Email already exists"

        hashed_password = hash_password(password)
        if hashed_password is None:
            return None, "Failed to hash password"

        try:
            user_id = self.user_model.create_user_db(name, email, hashed_password)
            return user_id, None
        except sqlite3.IntegrityError as e:
            
            return None, "Database integrity error during creation."
        except Exception as e:
            print(f"Error creating user: {e}")
            return None, "An unexpected error occurred during user creation."

    def update_user(self, user_id, name=None, email=None):
        if not name and not email:
            return False, "No data to update"

        try:
            existing_user = self.user_model.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error fetching existing user in update_user service: {e}")
            return False, "An error occurred while fetching user details for update."

        if not existing_user:
            return False, "User not found."

        # Check name for uniqueness if it's being changed
        if name and name != existing_user['name']:
            conflicting_user_by_name = self.user_model.get_user_by_name(name)
            if conflicting_user_by_name and conflicting_user_by_name['id'] != user_id:
                return False, "Name already exists for another user"
        
        # Check email for uniqueness if it's being changed
        if email and email.lower() != existing_user['email']:
            conflicting_user_by_email = self.user_model.get_user_by_email(email.lower())
            if conflicting_user_by_email and conflicting_user_by_email['id'] != user_id:
                return False, "Email already exists for another user"

        name_to_update = name if name is not None else existing_user['name']
        email_to_update = email.lower() if email is not None else existing_user['email']
        
        try:
            success = self.user_model.update_user_db(user_id, name_to_update, email_to_update)
            return success, None
        except Exception as e:
            print(f"Error updating user: {e}")
            return False, "An unexpected error occurred during user update."

    def delete_user(self, user_id):
        return self.user_model.delete_user_db(user_id)

    def search_users(self, name_query):
        return self.user_model.search_users_by_name_db(name_query)

    def authenticate_user(self, email, password):
        user_data = self.user_model.get_user_by_email(email)
        if user_data and check_password(password, user_data['password']):
            return user_data['id'], True, None
        else:
            return None, False, "Invalid email or password."