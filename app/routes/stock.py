# app/routes/stock.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.stock_service import fetch_ticker_details, get_ticker_tape
from app.services.stock_service import search_ticker_in_db

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/ticker', methods=['GET'])
def get_ticker_details():
    """
    API endpoint to fetch details of a stock ticker.

    Example: /ticker?ticker=AAPL
    """
    ticker = request.args.get('ticker')

    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    data = fetch_ticker_details(ticker)

    if data is None:
        return jsonify({"error": "Could not fetch ticker details"}), 404

    return jsonify(data), 200


@stock_bp.route('/search', methods=['GET'])
def search_stocks():
    """
    API endpoint to search for stocks by ticker symbol or company name from the local database.

    Example: /search?query=AAPL
    """
    query = request.args.get('query')

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    results = search_ticker_in_db(query)

    return jsonify(results), 200


@stock_bp.route('/ticker-tape', methods=['GET'])
def ticker_tape_endpoint():
    """
    API endpoint to fetch ticker tape data for major stocks.

    Example: /ticker-tape
    """
    try:
        data = get_ticker_tape()
        return jsonify(data), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching ticker tape data.", "details": str(e)}), 500
