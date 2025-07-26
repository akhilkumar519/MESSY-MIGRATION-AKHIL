import pytest # type: ignore
from app import create_app
import sqlite3
import os
from application.database import init_db, get_db 

TEST_DB = 'test_users.db'

@pytest.fixture
def client():
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE'] = TEST_DB 
    app.config['SECRET_KEY'] = 'test_secret_key' 

    # Initializing  the test database
    with app.app_context():
        # Ensure a clean path for each test
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        
       
        init_db() 

        
        db = get_db()
        cursor = db.cursor()
        from application.utils.security import hash_password 
        
        sample_users = [
            ("Alice Smith", "alice@example.com", "password123"),
            ("Bob Johnson", "bob@example.com", "securepass"),
            ("Charlie Brown", "charlie@example.com", "mysecret")
        ]

        for name, email, password in sample_users:
            hashed_pw = hash_password(password)
            if hashed_pw:
                try:
                    cursor.execute(
                        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                        (name, email, hashed_pw)
                    )
                except Exception as e:
                    print(f"Error adding test user {name} during fixture setup: {e}")
            else:
                print(f"Failed to hash password for test user {name} during fixture setup.")
        db.commit()
        

    with app.test_client() as client:
        yield client 

    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def add_test_user(client, name, email, password):
    
    from application.services.user_service import UserService
    user_service_for_test = UserService()
    with client.application.app_context():
        user_id, error = user_service_for_test.create_user(name, email, password)
        if error:
            raise Exception(f"Failed to add test user: {error}")
        return user_id


# --- Test Cases ---

def test_home_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"User Management System API is Running!" in response.data

def test_global_404_not_found(client):
    """Test that invalid endpoints return a consistent JSON 404 error."""
    response = client.get('/nonexistent_route')
    assert response.status_code == 404
    assert response.json['message'] == "Invalid endpoint."

def test_global_405_method_not_allowed(client):
    """Test that unsupported methods on valid routes return a consistent JSON 405 error."""
    response = client.put('/users', json={})
    assert response.status_code == 405
    assert response.json['message'] == "Method not allowed for this resource."

def test_create_user_success(client):
    """Test successful user creation with all valid fields."""
    user_data = {"name": "Test User", "email": "test@example.com", "password": "Password123"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 201
    assert response.json['message'] == "User created successfully."
    assert "user_id" in response.json



def test_create_user_missing_multiple_fields(client):
    """Test user creation with multiple missing required fields."""
    user_data = {"name": "Missing Some"} # Missing email and password
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    
    assert response.json['message'] == "Missing required fields: email, password"

def test_create_user_empty_fields(client):
    """Test user creation with empty string required fields (triggers general missing fields)."""
    user_data = {"name": "", "email": "", "password": ""}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    
    assert response.json['message'] == "Missing required fields: name, email, password"

def test_create_user_name_too_short(client):
    """Test user creation with name less than 2 characters."""
    user_data = {"name": "A", "email": "shortname@example.com", "password": "Password123"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    assert response.json['message'] == "Name must be at least 2 characters long."

def test_create_user_invalid_email_format(client):
    """Test user creation with invalid email format (regex)."""
    user_data = {"name": "User Bad Email", "email": "bademail.com", "password": "Password123"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    assert response.json['message'] == "Invalid email format provided."

def test_create_user_password_too_short(client):
    """Test user creation with password less than 8 characters."""
    user_data = {"name": "ShortPass", "email": "shortpass@example.com", "password": "Pass1"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    assert response.json['message'] == "Password must be at least 8 characters long."

def test_create_user_password_no_uppercase(client):
    """Test user creation with password missing uppercase letter."""
    user_data = {"name": "NoUpper", "email": "noupper@example.com", "password": "password123"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    assert response.json['message'] == "Password must contain at least one uppercase letter."

def test_create_user_password_no_lowercase(client):
    """Test user creation with password missing lowercase letter."""
    user_data = {"name": "NoLower", "email": "NOLOWER@EXAMPLE.COM", "password": "PASSWORD123"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    assert response.json['message'] == "Password must contain at least one lowercase letter."

def test_create_user_password_no_number(client):
    """Test user creation with password missing a number."""
    user_data = {"name": "NoNumber", "email": "nonumber@example.com", "password": "Passwordabc"}
    response = client.post('/users', json=user_data)
    assert response.status_code == 400
    assert response.json['message'] == "Password must contain at least one number."

def test_create_user_duplicate_email(client):
    """Test user creation with an email that already exists (from init_db.py)."""
    user_data = {"name": "Unique Name", "email": "alice@example.com", "password": "Password123"}
    # Alice's email already exists from init_db.py's sample data
    response = client.post('/users', json=user_data)
    assert response.status_code == 409 # Conflict
    assert response.json['message'] == "This email is already registered." # Message for email conflict



def test_get_all_users(client):
    """Test retrieving all users."""
    # Now expecting at least 3 users from init_db.py sample data
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 3 # Expect at least 3 initial users
    assert any(user['name'] == "Alice Smith" for user in response.json)
    assert any(user['email'] == "bob@example.com" for user in response.json)
    assert not any('password' in user for user in response.json)

def test_get_user_by_id_success(client):
    """Test retrieving a specific user by ID."""
    response = client.get('/user/1') # Alice's ID from init_db.py
    assert response.status_code == 200
    assert response.json['name'] == "Alice Smith"
    assert response.json['email'] == "alice@example.com"
    assert not 'password' in response.json

def test_get_user_by_id_not_found(client):
    """Test retrieving a non-existent user."""
    response = client.get('/user/9999')
    assert response.status_code == 404
    assert response.json['message'] == "User not found."

# --- MODIFIED/NEW TESTS: Update User Validation

def test_update_user_success(client):
    """Test successful user update of name and email."""
    # Use existing user 1 (Alice)
    update_data = {"name": "Alice Wonderland", "email": "alice.wonderland@example.com"}
    response = client.put('/user/1', json=update_data)
    assert response.status_code == 200
    assert response.json['message'] == "User updated successfully."

    # Verify update
    updated_user = client.get('/user/1').json
    assert updated_user['name'] == "Alice Wonderland"
    assert updated_user['email'] == "alice.wonderland@example.com"

def test_update_user_partial(client):
    """Test partial user update (only name)."""
    # Use existing user 2 (Bob)
    update_data = {"name": "Robert Johnson"}
    response = client.put('/user/2', json=update_data)
    assert response.status_code == 200
    assert response.json['message'] == "User updated successfully."

    # Verify update
    updated_user = client.get('/user/2').json
    assert updated_user['name'] == "Robert Johnson"
    assert updated_user['email'] == "bob@example.com" # Email should remain unchanged

def test_update_user_not_found(client):
    """Test updating a non-existent user."""
    update_data = {"name": "Non Existent"}
    response = client.put('/user/9999', json=update_data)
    assert response.status_code == 404
    assert response.json['message'] == "User not found."

def test_update_user_invalid_data(client):
    """Test update with invalid data (e.g., empty name)."""
    # Use existing user 1
    update_data = {"name": ""}
    response = client.put('/user/1', json=update_data)
    assert response.status_code == 400
    assert response.json['message'] == "Name must be a non-empty string if provided."

def test_update_user_duplicate_email_conflict(client):
    """Test updating a user's email to one already in use by another user."""
    # User 1 (Alice) tries to take User 2's (Bob's) email
    update_data = {"email": "bob@example.com"}
    response = client.put('/user/1', json=update_data)
    assert response.status_code == 409
    assert response.json['message'] == "The provided email is already in use by another user."




def test_delete_user_success(client):
    """Test successful user deletion."""
    # Create a user to delete specifically for this test
    user_id_to_delete = add_test_user(client, "Delete Me", "deleteme@example.com", "DeletePass123")
    response = client.delete(f'/user/{user_id_to_delete}')
    assert response.status_code == 200
    assert response.json['message'] == f"User with ID {user_id_to_delete} deleted successfully."

    # Verify deletion
    verify_response = client.get(f'/user/{user_id_to_delete}')
    assert verify_response.status_code == 404
    assert verify_response.json['message'] == "User not found."

def test_delete_user_not_found(client):
    """Test deleting a non-existent user."""
    response = client.delete('/user/9999')
    assert response.status_code == 404
    assert response.json['message'] == "User not found."

def test_search_users_success(client):
    """Test searching for users by name."""
    
    response = client.get('/search?name=john')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json[0]['name'] == "Bob Johnson"

    response = client.get('/search?name=alic')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
    assert response.json[0]['name'] == "Alice Smith"

def test_search_users_no_results(client):
    """Test search with no matching users."""
    response = client.get('/search?name=NonExistent')
    assert response.status_code == 200
    assert response.json['message'] == "No users found matching your criteria."

def test_search_users_no_query_param(client):
    """Test search without providing a name parameter."""
    response = client.get('/search')
    assert response.status_code == 400
    assert response.json['message'] == "Search query 'name' parameter is required and must not be empty."

def test_login_success(client):
    """Test successful user login."""
    login_data = {"email": "alice@example.com", "password": "password123"}
    response = client.post('/login', json=login_data)
    assert response.status_code == 200
    assert response.json['status'] == "success"
    assert response.json['user_id'] == 1 
    assert response.json['message'] == "Login successful."

def test_login_failed_wrong_password(client):
    """Test login with incorrect password."""
    login_data = {"email": "alice@example.com", "password": "wrongpassword"}
    response = client.post('/login', json=login_data)
    assert response.status_code == 401
    assert response.json['message'] == "Invalid email or password."

def test_login_failed_user_not_found(client):
    """Test login with non-existent email."""
    login_data = {"email": "nonexistent@example.com", "password": "anypass"}
    response = client.post('/login', json=login_data)
    assert response.status_code == 401
    assert response.json['message'] == "Invalid email or password."

def test_login_missing_fields(client):
    """Test login with missing required fields."""
    login_data = {"email": "incomplete@example.com"}
    response = client.post('/login', json=login_data)
    assert response.status_code == 400
    assert response.json['message'] == "Missing required field: 'password'."