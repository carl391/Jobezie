"""
Pytest Configuration and Fixtures

Provides shared fixtures for testing the Jobezie application.
"""

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Provide database session for tests."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('TestPassword123')
        db.session.add(user)
        db.session.commit()

        # Refresh to get the ID
        db.session.refresh(user)

        yield user
        # Cleanup handled by app fixture's db.drop_all()


@pytest.fixture(scope='function')
def test_user_pro(app):
    """Create a test user with Pro subscription."""
    with app.app_context():
        user = User(
            email='pro@example.com',
            first_name='Pro',
            last_name='User',
            subscription_tier='pro'
        )
        user.set_password('TestPassword123')
        db.session.add(user)
        db.session.commit()

        db.session.refresh(user)

        yield user
        # Cleanup handled by app fixture's db.drop_all()


@pytest.fixture(scope='function')
def auth_headers(app, test_user):
    """Create authorization headers for test user."""
    with app.app_context():
        access_token = create_access_token(identity=str(test_user.id))
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture(scope='function')
def auth_headers_pro(app, test_user_pro):
    """Create authorization headers for pro user."""
    with app.app_context():
        access_token = create_access_token(identity=str(test_user_pro.id))
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture
def sample_user_data():
    """Sample user registration data."""
    return {
        'email': 'newuser@example.com',
        'password': 'SecurePass123',
        'first_name': 'New',
        'last_name': 'User'
    }


@pytest.fixture
def sample_login_data():
    """Sample login data matching test_user."""
    return {
        'email': 'test@example.com',
        'password': 'TestPassword123'
    }


class AuthActions:
    """Helper class for authentication actions in tests."""

    def __init__(self, client):
        self._client = client

    def register(self, email='test@example.com', password='TestPassword123', **kwargs):
        """Register a new user."""
        data = {
            'email': email,
            'password': password,
            **kwargs
        }
        return self._client.post(
            '/api/auth/register',
            json=data,
            content_type='application/json'
        )

    def login(self, email='test@example.com', password='TestPassword123'):
        """Login a user."""
        return self._client.post(
            '/api/auth/login',
            json={'email': email, 'password': password},
            content_type='application/json'
        )

    def logout(self, token):
        """Logout a user."""
        return self._client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )


@pytest.fixture
def auth(client):
    """Provide auth helper for tests."""
    return AuthActions(client)
