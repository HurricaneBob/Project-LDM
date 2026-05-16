import os

import pytest

os.environ["LLM_MOCK"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app
from models.extensions import db


@pytest.fixture
def app():
    application = create_app()
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["TESTING"] = True
    with application.app_context():
        db.create_all()
        from scripts.seed_db import seed_database

        seed_database(force=True)
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
