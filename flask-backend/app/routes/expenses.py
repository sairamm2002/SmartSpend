from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Expense, Category
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/', methods=['GET'])
@jwt_required()
def get_expenses():
    # Convert JWT identity from string to int
    user_id = int(get_jwt_identity())
    query = Expense.query.filter_by(user_id=user_id)

    # Filtering - all parameters optional with proper error handling
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')
    search = request.args.get('search')

    if start_date:
        try:
            query = query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        except (ValueError, TypeError):
            pass
    
    if end_date:
        try:
            query = query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        except (ValueError, TypeError):
            pass
    
    if category_id:
        try:
            query = query.filter_by(category_id=int(category_id))
        except (ValueError, TypeError):
            pass
    
    if min_amount:
        try:
            query = query.filter(Expense.amount >= float(min_amount))
        except (ValueError, TypeError):
            pass
    
    if max_amount:
        try:
            query = query.filter(Expense.amount <= float(max_amount))
        except (ValueError, TypeError):
            pass
    
    if search:
        query = query.filter(Expense.description.ilike(f'%{search}%'))

    # Sorting
    sort_by = request.args.get('sort_by', 'date')
    order = request.args.get('order', 'desc')
    
    if sort_by == 'date':
        if order == 'asc':
            query = query.order_by(Expense.date.asc())
        else:
            query = query.order_by(Expense.date.desc())
    elif sort_by == 'amount':
        if order == 'asc':
            query = query.order_by(Expense.amount.asc())
        else:
            query = query.order_by(Expense.amount.desc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if per_page > 100:
        per_page = 100
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [e.to_dict() for e in paginated.items],
        'total': paginated.total,
        'page': page,
        'pages': paginated.pages
    }), 200

@expenses_bp.route('/', methods=['POST'])
@jwt_required()
def create_expense():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    amount = data.get('amount')
    category_id = data.get('category_id')
    description = data.get('description', '')
    date_str = data.get('date')

    if not amount or not category_id:
        return jsonify({'error': 'Amount and category are required'}), 400

    cat = Category.query.filter(
        (Category.id == category_id) & 
        ((Category.user_id == user_id) | (Category.user_id.is_(None)))
    ).first()
    if not cat:
        return jsonify({'error': 'Invalid category'}), 400

    try:
        amount = float(amount)
    except:
        return jsonify({'error': 'Invalid amount'}), 400

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
    except:
        date = datetime.utcnow().date()

    expense = Expense(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        description=description,
        date=date
    )
    db.session.add(expense)
    db.session.commit()

    return jsonify(expense.to_dict()), 201

@expenses_bp.route('/<int:exp_id>', methods=['GET'])
@jwt_required()
def get_expense(exp_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.filter_by(id=exp_id, user_id=user_id).first()
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    return jsonify(expense.to_dict()), 200

@expenses_bp.route('/<int:exp_id>', methods=['PUT'])
@jwt_required()
def update_expense(exp_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.filter_by(id=exp_id, user_id=user_id).first()
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    data = request.get_json()
    if 'amount' in data:
        try:
            expense.amount = float(data['amount'])
        except:
            return jsonify({'error': 'Invalid amount'}), 400
    
    if 'category_id' in data:
        cat = Category.query.filter(
            (Category.id == data['category_id']) & 
            ((Category.user_id == user_id) | (Category.user_id.is_(None)))
        ).first()
        if not cat:
            return jsonify({'error': 'Invalid category'}), 400
        expense.category_id = data['category_id']
    
    if 'description' in data:
        expense.description = data['description']
    
    if 'date' in data:
        try:
            expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except:
            return jsonify({'error': 'Invalid date format'}), 400

    db.session.commit()
    return jsonify(expense.to_dict()), 200

@expenses_bp.route('/<int:exp_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(exp_id):
    user_id = int(get_jwt_identity())
    expense = Expense.query.filter_by(id=exp_id, user_id=user_id).first()
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({'message': 'Expense deleted'}), 200