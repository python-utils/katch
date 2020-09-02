import pytest

from flask import Blueprint, Flask


@pytest.fixture
def app():
    app = Flask(__name__)
    yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def blueprint(app):
    yield Blueprint("api", __name__, url_prefix="/api/v1/")
