from flask import Blueprint, request, jsonify # type: ignore
import json
import re
from application.services.user_service import UserService

user_bp = Blueprint('user_bp', __name__)
user_service = UserService()

def _validate_json_input(data, required_fields=None):
    if not data:
        return "No input data provided."
    if required_fields:
        for field in required_fields:
            if field not in data:
                return f"Missing required field: '{field}'."
            if not isinstance(data[field], str) or not data[field].strip():
                return f"Field '{field}' must be a non-empty string."
    return None

@user_bp.route('/users', methods=['GET'])
def get_all_users_route():
    users = user_service.get_all_users()
    return jsonify(users), 200

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_route(user_id):
    user = user_service.get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "User not found."}), 404



@user_bp.route('/users', methods=['POST'])
def create_user_route():
    data = request.get_json()

    # Check for missing fields
    required_fields = ['name', 'email', 'password']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return jsonify({"message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    name = data['name'].strip()
    email = data['email'].strip()
    password = data['password'] 

    #  Validate Name format and length
    if len(name) < 2:
        return jsonify({"message": "Name must be at least 2 characters long."}), 400

    # Validate Email format using regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format provided."}), 400

    # Validate Password complexity
    # Conditions: min 8 chars, at least one uppercase, one lowercase, one number
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long."}), 400
    if not re.search(r'[A-Z]', password):
        return jsonify({"message": "Password must contain at least one uppercase letter."}), 400
    if not re.search(r'[a-z]', password):
        return jsonify({"message": "Password must contain at least one lowercase letter."}), 400
    if not re.search(r'\d', password):
        return jsonify({"message": "Password must contain at least one number."}), 400

    # Call the service to create the user (handles DB uniqueness checks)
    user_id, service_error = user_service.create_user(name, email, password)

    # Handle the response from the service
    if user_id:
        return jsonify({"message": "User created successfully.", "user_id": user_id}), 201
    else:
        # Handle specific uniqueness conflicts (409 Conflict)
        if service_error == "Email already exists":
            return jsonify({"message": "This email is already registered."}), 409
        if service_error == "Name already exists":
            return jsonify({"message": "This name is already taken."}), 409
        
        # Handle server-side errors (500 Internal Server Error)
        if service_error == "Failed to hash password":
             return jsonify({"message": "Password processing failed. Please try again."}), 500
        else:
             return jsonify({"message": service_error or "User creation failed due to an unexpected server issue."}), 500
@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user_route(user_id):
    data = request.get_json()
    error_message = _validate_json_input(data)
    if error_message:
        return jsonify({"message": error_message}), 400

    name = data.get('name')
    email = data.get('email')

    if name is None and email is None:
        return jsonify({"message": "At least 'name' or 'email' must be provided for update."}), 400

    if name is not None and (not isinstance(name, str) or not name.strip()):
        return jsonify({"message": "Name must be a non-empty string if provided."}), 400
    if email is not None and (not isinstance(email, str) or not email.strip() or '@' not in email.strip()):
        return jsonify({"message": "Invalid email format if provided."}), 400

    success, service_error = user_service.update_user(user_id, name.strip() if name else None, email.strip() if email else None)

    if success:
        return jsonify({"message": "User updated successfully."}), 200
    else:
        if service_error == "User not found.": # Match the exact message from service
            return jsonify({"message": service_error}), 404
        elif service_error == "Email already exists for another user":
            return jsonify({"message": "The provided email is already in use by another user."}), 409
        elif service_error == "No data to update":
             return jsonify({"message": service_error}), 400
        else:
            return jsonify({"message": service_error or "User update failed due to an unexpected server issue."}), 500

@user_bp.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    if user_service.delete_user(user_id):
        return jsonify({"message": f"User with ID {user_id} deleted successfully."}), 200
    else:
        return jsonify({"message": "User not found."}), 404

@user_bp.route('/search', methods=['GET'])
def search_users_route():
    name_query = request.args.get('name')
    if not name_query or not isinstance(name_query, str) or not name_query.strip():
        return jsonify({"message": "Search query 'name' parameter is required and must not be empty."}), 400

    users = user_service.search_users(name_query.strip())
    if not users:
        return jsonify({"message": "No users found matching your criteria."}), 200
    else:
        return jsonify(users), 200

@user_bp.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    error_message = _validate_json_input(data, ['email', 'password'])
    if error_message:
        return jsonify({"message": error_message}), 400

    if '@' not in data['email'].strip() or '.' not in data['email'].strip():
        return jsonify({"message": "Invalid email format provided."}), 400

    email = data['email'].strip()
    password = data['password'].strip()

    user_id, authenticated, service_error = user_service.authenticate_user(email, password)

    if authenticated:
        return jsonify({"status": "success", "user_id": user_id, "message": "Login successful."}), 200
    else:
        return jsonify({"message": service_error}), 401