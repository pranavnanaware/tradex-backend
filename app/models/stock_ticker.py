from ..extensions import db
from datetime import datetime


class StockTicker(db.Model):
    __tablename__ = 'stock_ticker'

    id = db.Column(db.Integer, autoincrement=True)
    symbol = db.Column(db.String(10), nullable=False,
                       unique=True, primary_key=True)

    def __repr__(self):
        return f'<StockTicker {self.symbol}>'
