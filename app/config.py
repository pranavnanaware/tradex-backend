import os
import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI_CONNECTION')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'Pranav@123'
