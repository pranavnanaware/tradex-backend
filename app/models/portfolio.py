# app/models/portfolio.py
from ..extensions import db


class Portfolio(db.Model):
    __tablename__ = 'portfolio_view'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(10), nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)
    average_price = db.Column(db.Float, nullable=False)

    # Ensure that each user can only have one unique ticker in their portfolio
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'ticker', name='_user_ticker_uc'),)
