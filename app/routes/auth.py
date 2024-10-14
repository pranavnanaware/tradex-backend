# app/routes/auth.py
from flask import Blueprint, make_response, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..models.user import User

# Create a Blueprint for the authentication routes
auth_bp = Blueprint('auth', __name__)

# Registration Endpoint
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    # Check if all required fields are provided
    if not all([email, password, name]):
        return jsonify({"error": "All fields are required"}), 400

    print(email, password, name)
    try:
        # Check if user already exists
        if User.query.filter((User.email == email)).first():
            return jsonify({"error": "User with this username or email already exists"}), 409

        # Create new user
        new_user = User(
            email=email,
            name=name
        )
        new_user.set_password(password)  # Hash the password

        db.session.add(new_user)  # Add new user to the session
        db.session.commit()  # Commit the session to the database

        return jsonify({"message": "User registered successfully"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback the session in case of error
        return jsonify({"error": "Something went wrong"}), 500

# Login Endpoint
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Check if both email and password are provided
    if not all([email, password]):
        return jsonify({"error": "Username and password are required"}), 400

    try:
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid username or password"}), 401

        # Create JWT token with no expiration
        access_token = create_access_token(
            identity=user.id, expires_delta=False)

        # Create a response and set the JWT in an HttpOnly cookie
        response = make_response(jsonify({"message": "Login successful"}), 200)
        set_access_cookies(response, access_token)

        return response

    except SQLAlchemyError as e:
        return jsonify({"error": "You need to sign-up"}), 500

# Get User Endpoint
@auth_bp.route('/user', methods=['GET'])
@jwt_required()  # Require a valid JWT token to access this route
def get_user():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

    user = User.query.get(user_id)  # Query the user from the database

    if user:
        return jsonify({
            "id": user.id,
            "email": user.email,
            "name": user.name
        }), 200
    else:
        return jsonify({"error": "User not found"}), 404

# Logout Endpoint
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()  # Require a valid JWT token to access this route
def logout():
    response = make_response(jsonify({"message": "Logout successful"}), 200)
    print('logout')
    unset_jwt_cookies(get_jwt_identity())  # Unset the JWT cookies
    return response
