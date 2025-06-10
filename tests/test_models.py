from app.models import User

def test_new_user(new_user):
    assert new_user.username == 'testuser'
    assert new_user.email == 'test@example.com'
    assert new_user.check_password('testpassword')
    assert not new_user.check_password('wrongpassword')
    assert not new_user.is_admin
    assert new_user.google_sheet_id is None

def test_set_password(new_user):
    new_user.set_password('newpassword')
    assert new_user.check_password('newpassword')
    assert not new_user.check_password('testpassword')
