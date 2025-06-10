from flask import url_for

def test_app_exists(app):
    assert app is not None

def test_index_anonymous(client):
    # Anonymous users should be redirected from '/' to login page
    response = client.get(url_for('main.index'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data # Check for login page content

def test_index_authenticated(logged_in_client): # logged_in_client from conftest
    response = logged_in_client.get(url_for('main.index'))
    assert response.status_code == 200
    assert b"Hi, testuser!" in response.data
    assert b"Your Workout Program" in response.data # Check for user dashboard content
