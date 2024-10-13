# app/models/user.py
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(80), nullable=False)
    cash_balance = db.Column(db.Float, nullable=False,
                             default=10000.0, server_default='10000.0')
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    portfolio = db.relationship('Portfolio', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
