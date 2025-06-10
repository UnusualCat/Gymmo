import pytest
import os
from app import create_app, db
from app.models import User

# Use a separate SQLite database for testing
TEST_DB_PATH = 'test_app.sqlite'

@pytest.fixture(scope='session')
def app():
    # Create a temporary instance path for testing if it doesn't exist
    instance_path = os.path.join(os.getcwd(), 'test_instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": 'sqlite:///' + os.path.join(instance_path, TEST_DB_PATH),
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for simpler form testing in unit tests
        "LOGIN_DISABLED": False, # Ensure login is not disabled for auth tests
        "SERVER_NAME": "localhost.localdomain" # Required for url_for outside of request context
    })

    # Ensure service_account.json doesn't interfere if not mocked, place dummy if needed by a check
    # For robust tests, google_services should be mocked.
    # Path to dummy service account file in test_instance
    dummy_service_account_path = os.path.join(instance_path, 'service_account.json')
    if not os.path.exists(dummy_service_account_path):
        with open(dummy_service_account_path, 'w') as f:
            f.write('{"type": "service_account", "comment": "dummy for testing"}')


    with app.app_context():
        db.create_all()
        yield app # provide the app object for tests
        db.drop_all() # clean up the database after tests run

    # Clean up the dummy instance folder and test db
    if os.path.exists(os.path.join(instance_path, TEST_DB_PATH)):
        os.remove(os.path.join(instance_path, TEST_DB_PATH))
    if os.path.exists(dummy_service_account_path):
        os.remove(dummy_service_account_path)
    if os.path.exists(instance_path) and not os.listdir(instance_path): # if empty
        os.rmdir(instance_path)


@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def new_user(app):
    with app.app_context(): # Ensure we are in app context for db operations
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture(scope='function')
def logged_in_client(client, new_user):
    # Log in the new_user
    # Note: Flask-Login's login_user needs a request context.
    # This direct post is simpler for basic tests. For complex scenarios, consider flask_login.utils.login_user within a test request context.
    client.post('/auth/login', data={
        'username': new_user.username,
        'password': 'testpassword'
    }, follow_redirects=True)
    return client
