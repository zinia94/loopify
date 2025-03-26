import os
import pytest
from unittest.mock import patch, MagicMock
from app.utils.helpers import save_image, get_userinfo_from_session
from app.models.user import User
from app import create_app
import shutil
from flask import session
from flask_login import login_user, logout_user

os.environ["FLASK_ENV"] = "testing"

app_config = {
    "DEFAULT_IMAGE_URL": "/static/images/default.jpg",
    "IMAGE_UPLOAD_FOLDER": "static/uploads/images",
    "ROOT_DIR": "tests",
}


@pytest.fixture
def app():
    app = create_app()

    # cleanup before test
    with app.app_context():
        upload_dir = os.path.join(app_config["ROOT_DIR"], "static")
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        yield app

    # cleanup after test
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)


@pytest.fixture
def mock_session(app, monkeypatch):
    with app.test_request_context():
        user = User(username="test_user")
        user.set_id("123")
        user.set_password("test_password")
        login_user(user)
        session["total_cart_items"] = 5
        monkeypatch.setattr("flask.session", session)
        yield session
        logout_user


def test_save_image_without_image(app):
    with app.app_context():
        with patch("flask.current_app.config", app_config):
            result = save_image(None)
            assert result == app_config["DEFAULT_IMAGE_URL"]


def test_save_image_with_image(app):
    mock_image = MagicMock()
    mock_image.filename = "test_image.jpg"
    with app.app_context():
        with patch("flask.current_app.config", app_config):
            result = save_image(mock_image)
            assert result.startswith(f"/{app_config['IMAGE_UPLOAD_FOLDER']}/")
            image_path = os.path.join(
                app_config["ROOT_DIR"], app_config["IMAGE_UPLOAD_FOLDER"]
            )
            assert os.path.exists(image_path)


def test_get_userinfo_from_session(mock_session):
    userinfo = get_userinfo_from_session()
    assert userinfo.user_id == "123"
    assert userinfo.username == "test_user"
    assert userinfo.total_cart_items == mock_session["total_cart_items"]
