from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Category, Expense

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = int(get_jwt_identity())
    user_cats = Category.query.filter_by(user_id=user_id).all()
    global_cats = Category.query.filter_by(user_id=None, is_default=True).all()
    categories = user_cats + global_cats
    return jsonify([cat.to_dict() for cat in categories]), 200

@categories_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name')
    color = data.get('color', '#3b82f6')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    if Category.query.filter_by(user_id=user_id, name=name).first():
        return jsonify({'error': 'Category already exists'}), 409

    cat = Category(user_id=user_id, name=name, color=color, is_default=False)
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201

@categories_bp.route('/<int:cat_id>', methods=['PUT'])
@jwt_required()
def update_category(cat_id):
    user_id = int(get_jwt_identity())
    cat = Category.query.filter_by(id=cat_id, user_id=user_id).first()
    if not cat:
        return jsonify({'error': 'Category not found'}), 404

    data = request.get_json()
    if 'name' in data:
        existing = Category.query.filter_by(user_id=user_id, name=data['name']).first()
        if existing and existing.id != cat_id:
            return jsonify({'error': 'Category name already exists'}), 409
        cat.name = data['name']
    if 'color' in data:
        cat.color = data['color']

    db.session.commit()
    return jsonify(cat.to_dict()), 200

@categories_bp.route('/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_category(cat_id):
    user_id = int(get_jwt_identity())
    cat = Category.query.filter_by(id=cat_id, user_id=user_id).first()
    if not cat:
        return jsonify({'error': 'Category not found'}), 404

    if Expense.query.filter_by(category_id=cat_id).first():
        return jsonify({'error': 'Cannot delete category with existing expenses'}), 400

    db.session.delete(cat)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200