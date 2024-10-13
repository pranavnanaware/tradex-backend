from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import sessionmaker
from models.stock_ticker import StockTicker

# Database connection configuration
DATABASE_URI = 'postgresql://tsdbadmin:eh2ojpkovka403ja@qj44sm92lq.ey938hatod.tsdb.cloud.timescale.com:31413/tsdb?sslmode=require'

# TXT file path (replace with your file path)
TXT_FILE_PATH = 'all_tickers.txt'
engine = create_engine(DATABASE_URI)

Session = sessionmaker(bind=engine)
session = Session()

# Define a function to insert stock symbols from the TXT file into the database


def insert_symbols_from_txt(txt_file):
    try:
        # Read the TXT file and split the content by commas
        with open(txt_file, 'r') as file:
            symbols = file.read().split(',')

        # Strip any leading/trailing whitespace from symbols
        symbols = [symbol.strip() for symbol in symbols]

        # Insert each symbol into the database
        for symbol in symbols:
            # Check if the symbol already exists to avoid duplicates
            if session.query(StockTicker).filter_by(symbol=symbol).first() is None:
                stock_ticker = StockTicker(symbol=symbol)
                session.add(stock_ticker)

        # Commit the session to save all changes
        session.commit()

        print(f"Inserted {len(symbols)} symbols into the database.")

    except SQLAlchemyError as e:
        session.rollback()  # Roll back the session in case of an error
        print(
            f"An error occurred while inserting symbols into the database: {e}")
    finally:
        session.close()  # Close the session


if __name__ == "__main__":
    # Call the function to insert symbols
    insert_symbols_from_txt(TXT_FILE_PATH)
