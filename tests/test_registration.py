import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="function")
def setup_database():
    try:
        os.remove('users.db')
    except:
        pass
    create_db()
    yield

@pytest.fixture
def connection():
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()

def test_create_db(setup_database, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists

def test_add_new_user(setup_database, connection):
    result = add_user('testuser', 'testuser@example.com', 'password123')
    assert result is True
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user
    assert user[0] == 'testuser'
    assert user[1] == 'testuser@example.com'
    assert user[2] == 'password123'

def test_add_user_with_existing_username(setup_database):
    add_user('existinguser', 'user1@example.com', 'password123')
    result = add_user('existinguser', 'user2@example.com', 'differentpassword')
    assert result is False

def test_successful_authentication(setup_database):
    add_user('authuser', 'auth@example.com', 'correctpassword')
    result = authenticate_user('authuser', 'correctpassword')
    assert result is True

def test_authentication_nonexistent_user(setup_database):
    result = authenticate_user('nonexistentuser', 'anypassword')
    assert result is False

def test_authentication_wrong_password(setup_database):
    add_user('wrongpassuser', 'user@example.com', 'correctpassword')
    result = authenticate_user('wrongpassuser', 'wrongpassword')
    assert result is False

def test_display_users(setup_database, capsys):
    add_user('user1', 'user1@example.com', 'pass1')
    add_user('user2', 'user2@example.com', 'pass2')
    
    display_users()
    
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Логин: user1" in output
    assert "Электронная почта: user1@example.com" in output
    assert "Логин: user2" in output
    assert "Электронная почта: user2@example.com" in output

def test_multiple_users_can_be_added(setup_database, connection):
    users = [
        ('userA', 'usera@example.com', 'passA'),
        ('userB', 'userb@example.com', 'passB'),
        ('userC', 'userc@example.com', 'passC')
    ]
    
    for username, email, password in users:
        result = add_user(username, email, password)
        assert result is True
    
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    assert count == 3

def test_user_data_integrity(setup_database, connection):
    add_user('integrityuser', 'test@example.com', 'mypassword')
    
    cursor = connection.cursor()
    cursor.execute("SELECT username, email, password FROM users WHERE username='integrityuser'")
    user = cursor.fetchone()
    
    assert user is not None
    assert user[0] == 'integrityuser'
    assert user[1] == 'test@example.com'
    assert user[2] == 'mypassword'
