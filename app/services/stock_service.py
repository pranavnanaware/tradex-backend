# app/services/stock_service.py
from datetime import datetime, timedelta
import random
import yfinance as yf

from app.models.stock_ticker import StockTicker


def fetch_ticker_details(ticker):
    """
    Fetch stock ticker details from yfinance.

    :param ticker: The stock ticker symbol (e.g., "AAPL", "TSLA")
    :return: A dictionary with the stock details or None if the ticker is invalid.
    """
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        #

        return stock_info

    except Exception as e:
        print(f"Error fetching ticker details for {ticker}: {e}")
        return None


def search_ticker_in_db(query):
    """
    Search the stock_tickers table for matching symbols or company names.

    :param query: The search query for ticker symbol or company name.
    :return: A list of matching stock records.
    """
    try:
        search_query = f"%{query}%"
        results = StockTicker.query.filter(
            (StockTicker.symbol.ilike(search_query))
        ).all()

        data = [
            {
                "symbol": stock.symbol,
            } for stock in results
        ]
        return data
    except Exception as e:
        print(f"Error searching for ticker in DB: {e}")
        return []


def get_current_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        current_price = stock_info['currentPrice']
        return current_price
    except Exception as e:
        print(f"Error fetching ticker details for {ticker}: {e}")
        return None


def get_historical_prices(ticker, days=30):
    # Replace with actual implementation to fetch historical prices
    historical_prices = []
    base_price = get_current_price(ticker) or 100.0
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        # Simulate price changes
        price = base_price + random.uniform(-5, 5)
        historical_prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': round(price, 2)
        })
    # Return in chronological order
    return list(reversed(historical_prices))


def get_ticker_tape():
    """
    Fetches real-time ticker data for predefined stock symbols from major exchanges.

    Returns:
        list: A list of dictionaries containing Symbol, Price, and Change.
    """
    # Define a list of hard-coded tickers from major exchanges
    tickers = [
        "AAPL",  # Apple Inc. - NASDAQ
        "MSFT",  # Microsoft Corporation - NASDAQ
        "GOOGL",  # Alphabet Inc. - NASDAQ
        "AMZN",  # Amazon.com Inc. - NASDAQ
        "TSLA",  # Tesla Inc. - NASDAQ
        "FB",    # Meta Platforms, Inc. - NASDAQ
        "BRK-B",  # Berkshire Hathaway Inc. - NYSE
        "JPM",   # JPMorgan Chase & Co. - NYSE
        "V",     # Visa Inc. - NYSE
        "JNJ"    # Johnson & Johnson - NYSE
    ]

    ticker_tape = []

    # Fetch data for all tickers at once for efficiency
    data = yf.download(tickers, period="1d", interval="1m",
                       threads=True, group_by='ticker', progress=False)

    for ticker in tickers:
        try:
            ticker_data = data[ticker]
            latest = ticker_data.iloc[-1]
            previous_close = yf.Ticker(ticker).info['previousClose']
            price = latest['Close']
            change = price - previous_close
            change_percent = (change / previous_close) * \
                100 if previous_close else 0

            ticker_tape.append({
                "symbol": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2)
            })
        except Exception as e:
            # Handle cases where data might not be available
            ticker_tape.append({
                "symbol": ticker,
                "price": None,
                "change": None,
                "change_percent": None,
                "error": str(e)
            })

    return ticker_tape
