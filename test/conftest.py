import pytest

from flask import Flask


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
    bp = Blueprint("api", __name__, url_prefix="/")
    app.register_blueprint(bp)
    return bp
