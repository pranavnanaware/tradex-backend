# app/routes/portfolio.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta

from app.services.stock_service import get_current_price, get_historical_prices
from ..models.portfolio import Portfolio
from ..models.user import User
from ..models.transaction import Transaction
import yfinance as yf

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def view_portfolio():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

    user = User.query.get(user_id)  # Fetch the user from the database
    if not user:
        # Return error if user not found
        return jsonify({'error': 'User not found'}), 404

    # Fetch all portfolio entries for the user
    portfolio_entries = Portfolio.query.filter_by(user_id=user_id).all()
    portfolio = []
    squared_off_positions = []

    for entry in portfolio_entries:
        # Get the current price of the stock
        current_price = get_current_price(entry.ticker)
        if current_price is None:
            # Fallback to average price if current price is not available
            current_price = entry.average_price

        # Calculate total value of the position
        total_value = entry.total_quantity * current_price
        total_invested = entry.total_quantity * \
            entry.average_price  # Calculate total invested amount
        # Calculate profit/loss in dollars
        profit_loss_dollars = total_value - total_invested
        profit_loss_percent = (
            profit_loss_dollars / total_invested) * 100 if total_invested != 0 else 0  # Calculate profit/loss in percent

        # Fetch all transactions for this ticker
        transactions = Transaction.query.filter_by(
            user_id=user_id, ticker=entry.ticker
        ).order_by(Transaction.timestamp.desc()).all()
        transactions_list = [
            {
                'id': txn.id,
                'ticker': txn.ticker,  # Include ticker for clarity
                'quantity': txn.quantity,
                'transaction_type': txn.transaction_type,
                'price': txn.price,
                'timestamp': txn.timestamp.isoformat()
            }
            for txn in transactions
        ]

        portfolio_data = {
            'ticker': entry.ticker,
            'shares': entry.total_quantity,
            'average_price': entry.average_price,
            'current_price': current_price,
            'total_value': total_value,
            'profit_loss': {
                'dollars': profit_loss_dollars,
                'percent': round(profit_loss_percent, 2)
            },
            'transactions': transactions_list
        }

        if entry.total_quantity > 0:
            # Add to portfolio if shares are still held
            portfolio.append(portfolio_data)
        else:
            # Only include necessary fields for squared off positions
            squared_off_positions.append({
                'ticker': entry.ticker,
                'total_invested': total_invested,
                'total_returned': total_value,
                'profit_loss': {
                    'dollars': profit_loss_dollars,
                    'percent': round(profit_loss_percent, 2)
                },
                'transactions': transactions_list
            })

    # Prepare the response
    response = {
        'user_id': user_id,
        'portfolio': portfolio,
        'squared_off_positions': squared_off_positions
    }

    if hasattr(user, 'cash_balance'):
        # Include cash balance if available
        response['cash_balance'] = user.cash_balance

    return jsonify(response), 200  # Return the response as JSON


@portfolio_bp.route('/analytics', methods=['GET'])
@jwt_required()
def view_analytics():
    user_id = get_jwt_identity()  # Get the user ID from the JWT token

    user = User.query.get(user_id)  # Fetch the user from the database
    if not user:
        # Return error if user not found
        return jsonify({'error': 'User not found'}), 404

    # Fetch all portfolio entries for the user
    portfolio_entries = Portfolio.query.filter_by(user_id=user_id).all()

    portfolio = []
    squared_off_positions = []
    total_value = 0
    total_profit_loss = 0
    portfolio_composition = []
    stock_performance = []
    best_performer = None
    best_performance = -float('inf')

    # Fetch recent transactions (e.g., last 5)
    recent_transactions_query = Transaction.query.filter_by(
        user_id=user_id).order_by(Transaction.timestamp.desc()).limit(5).all()
    recent_transactions = [
        {
            'id': txn.id,
            'ticker': txn.ticker,
            'quantity': txn.quantity,
            'transaction_type': txn.transaction_type,
            'price': txn.price,
            'timestamp': txn.timestamp.isoformat()
        }
        for txn in recent_transactions_query
    ]

    for entry in portfolio_entries:
        # Get the current price of the stock
        current_price = get_current_price(entry.ticker)
        if current_price is None:
            # Fallback to average price if current price is not available
            current_price = entry.average_price

        total_entry_value = entry.total_quantity * \
            current_price  # Calculate total value of the position
        total_invested = entry.total_quantity * \
            entry.average_price  # Calculate total invested amount
        profit_loss_dollars = total_entry_value - \
            total_invested  # Calculate profit/loss in dollars
        profit_loss_percent = (
            profit_loss_dollars / total_invested) * 100 if total_invested != 0 else 0  # Calculate profit/loss in percent

        # Update totals
        total_value += total_entry_value
        total_profit_loss += profit_loss_dollars

        # Prepare portfolio composition data
        portfolio_composition.append({
            'name': entry.ticker,
            'value': total_entry_value
        })

        # Determine best performer
        if profit_loss_percent > best_performance:
            best_performance = profit_loss_percent
            best_performer = entry.ticker

        # Calculate stock performance (assuming you have historical prices)
        historical_prices = get_historical_prices(
            entry.ticker, days=30)
        if historical_prices:
            initial_price = historical_prices[0]['price']
            current_performance = (
                (current_price - initial_price) / initial_price) * 100
        else:
            current_performance = 0

        stock_performance.append({
            'name': entry.ticker,
            'performance': round(current_performance, 2)
        })

        # Fetch all transactions for this ticker
        transactions = Transaction.query.filter_by(
            user_id=user_id, ticker=entry.ticker
        ).order_by(Transaction.timestamp.desc()).all()
        transactions_list = [
            {
                'id': txn.id,
                'ticker': txn.ticker,  # Include ticker for clarity
                'quantity': txn.quantity,
                'transaction_type': txn.transaction_type,
                'price': txn.price,
                'timestamp': txn.timestamp.isoformat()
            }
            for txn in transactions
        ]

        portfolio_data = {
            'ticker': entry.ticker,
            'shares': entry.total_quantity,
            'average_price': entry.average_price,
            'current_price': current_price,
            'total_value': total_entry_value,
            'profit_loss': {
                'dollars': profit_loss_dollars,
                'percent': round(profit_loss_percent, 2)
            },
            'transactions': transactions_list
        }

        if entry.total_quantity > 0:
            # Add to portfolio if shares are still held
            portfolio.append(portfolio_data)
        else:
            # Only include necessary fields for squared off positions
            squared_off_positions.append({
                'ticker': entry.ticker,
                'total_invested': total_invested,
                'total_returned': total_entry_value,
                'profit_loss': {
                    'dollars': profit_loss_dollars,
                    'percent': round(profit_loss_percent, 2)
                },
                'transactions': transactions_list
            })

    # Calculate total stocks
    total_stocks = len(portfolio_composition)

    # Prepare performance data (e.g., monthly portfolio values)
    performance_data = []
    today = datetime.utcnow()
    for i in range(6):  # Last 6 months
        month_date = today - timedelta(days=30*i)
        month_date_str = month_date.strftime('%Y-%m-%d')

        # Calculate portfolio value on the given date
        portfolio_value_on_date = 0
        for entry in portfolio_entries:
            ticker = entry.ticker
            stock = yf.Ticker(ticker)
            historical_data = stock.history(
                start=month_date_str, end=month_date_str)
            if not historical_data.empty:
                historical_price = historical_data['Close'].iloc[0]
            else:
                historical_price = entry.average_price  # Fallback to average price if no data

            portfolio_value_on_date += entry.total_quantity * historical_price

        performance_data.append({
            'date': month_date_str,
            'value': portfolio_value_on_date
        })

    # Prepare the response
    response = {
        'totalValue': total_value,
        'totalStocks': total_stocks,
        'totalProfitLoss': total_profit_loss,
        'bestPerformer': best_performer,
        'recentTransactions': recent_transactions,
        'portfolioComposition': portfolio_composition,
        'performanceData': performance_data,
        'stockPerformance': stock_performance,
        'portfolio': portfolio,
        'squared_off_positions': squared_off_positions
    }

    if hasattr(user, 'cash_balance'):
        # Include cash balance if available
        response['cash_balance'] = user.cash_balance

    return jsonify(response), 200  # Return the response as JSON
