# app/routes/transactions.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from ..models.transaction import Transaction
from ..models.portfolio import Portfolio
from ..models.user import User

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/buy', methods=['POST'])
@jwt_required()
def buy_stock():
    data = request.get_json()
    ticker = data.get('ticker')
    quantity = data.get('quantity')
    price = data.get('price')

    # Input validation
    if not all([ticker, quantity, price]):
        return jsonify({'error': 'Missing required fields'}), 400

    if quantity <= 0 or price <= 0:
        return jsonify({'error': 'Quantity and price must be positive'}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # (Optional) Check if user has enough cash
    total_cost = quantity * price
    if hasattr(user, 'cash_balance'):
        if user.cash_balance < total_cost:
            return jsonify({'error': 'Insufficient funds'}), 400
        user.cash_balance -= total_cost

    try:
        # Create Transaction
        transaction = Transaction(
            user_id=user_id,
            ticker=ticker.upper(),
            quantity=quantity,
            transaction_type='BUY',
            price=price
        )
        db.session.add(transaction)

        # Update Portfolio
        portfolio = Portfolio.query.filter_by(
            user_id=user_id, ticker=ticker.upper()).first()
        if portfolio:
            # Calculate new average price
            new_total_quantity = portfolio.total_quantity + quantity
            new_average_price = (
                (portfolio.average_price * portfolio.total_quantity) + (price * quantity)) / new_total_quantity
            portfolio.total_quantity = new_total_quantity
            portfolio.average_price = new_average_price
        else:
            portfolio = Portfolio(
                user_id=user_id,
                ticker=ticker.upper(),
                total_quantity=quantity,
                average_price=price
            )
            db.session.add(portfolio)

        db.session.commit()

        return jsonify({'message': 'Stock bought successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Transaction failed', 'details': str(e)}), 500


@transactions_bp.route('/sell', methods=['POST'])
@jwt_required()
def sell_stock():
    data = request.get_json()
    ticker = data.get('ticker')
    quantity = data.get('quantity')
    price = data.get('price')

    # Input validation
    if not all([ticker, quantity, price]):
        return jsonify({'error': 'Missing required fields'}), 400

    if quantity <= 0 or price <= 0:
        return jsonify({'error': 'Quantity and price must be positive'}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    portfolio = Portfolio.query.filter_by(
        user_id=user_id, ticker=ticker.upper()).first()
    if not portfolio or portfolio.total_quantity < quantity:
        return jsonify({'error': 'Insufficient stock quantity to sell'}), 400

    try:
        # Create Transaction
        transaction = Transaction(
            user_id=user_id,
            ticker=ticker.upper(),
            quantity=quantity,
            transaction_type='SELL',
            price=price
        )
        db.session.add(transaction)

        # Update Portfolio
        portfolio.total_quantity -= quantity
        if portfolio.total_quantity == 0:
            db.session.delete(portfolio)
        else:
            # Average price remains unchanged on selling
            pass

        # (Optional) Update user's cash balance
        if hasattr(user, 'cash_balance'):
            total_revenue = quantity * price
            user.cash_balance += total_revenue

        db.session.commit()

        return jsonify({'message': 'Stock sold successfully'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Transaction failed', 'details': str(e)}), 500
