# app/utils/helpers.py
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from ..extensions import db


def check_database_extensions():
    try:
        # Execute the query to get installed extensions
        result = db.session.execute(
            text('SELECT extname, extversion FROM pg_extension;'))
        extensions = result.fetchall()

        # Log the installed extensions
        current_app.logger.info("Database extensions installed:")
        for ext in extensions:
            current_app.logger.info(f"{ext.extname}: {ext.extversion}")

        # Check if TimescaleDB extension is installed
        if not any(ext.extname == 'timescaledb' for ext in extensions):
            error_message = "TimescaleDB extension is not installed in the database."
            current_app.logger.error(error_message)
            raise Exception(error_message)
    except SQLAlchemyError as e:
        current_app.logger.error(
            f"An error occurred when checking database extensions: {e}")
        raise e
