from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, User, Category
from ..utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Create default categories for new user
    default_cats = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other']
    for cat in default_cats:
        db.session.add(Category(user_id=user.id, name=cat, is_default=True))
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Convert user.id to string for JWT
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    # Get user_id from JWT and convert back to int
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200