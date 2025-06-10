import pytest
from flask import url_for
from app.models import User
from app import db

def test_register_page(client):
    response = client.get(url_for('auth.register'))
    assert response.status_code == 200
    assert b"Register" in response.data

def test_register_user(client, app):
    response = client.post(url_for('auth.register'), data={
        'username': 'newbie',
        'email': 'newbie@example.com',
        'password': 'apassword'
    }, follow_redirects=True)
    assert response.status_code == 200 # Should redirect to index
    assert b"Hi, newbie!" in response.data # Assuming index shows username
    with app.app_context():
        user = User.query.filter_by(username='newbie').first()
        assert user is not None
        assert user.email == 'newbie@example.com'

def test_login_page(client):
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_login_logout(client, new_user): # new_user fixture from conftest
    # Test login
    response = client.post(url_for('auth.login'), data={
        'username': new_user.username,
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Hi, testuser!" in response.data
    assert b"Logout" in response.data

    # Test logout
    response = client.get(url_for('auth.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data # Should be redirected to login or see login link
    assert b"Logout" not in response.data
