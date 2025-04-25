import pytest
from unittest.mock import MagicMock, patch
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class User:
    def __init__(self, username, roles, mfa_enabled):
        self.username = username
        self.roles = roles
        self.mfa_enabled = mfa_enabled
        self.is_authenticated = False

class System:
    def __init__(self):
        self.users = {}
        self.tls_enabled = False
        self.encryption_key = os.urandom(32)

    def add_user(self, user):
        self.users[user.username] = user

    def authenticate(self, username, password, mfa_token=None):
        user = self.users.get(username)
        if not user:
            return False
        if user.mfa_enabled and mfa_token != 'valid_token':
            return False
        if password == 'correct_password':
            user.is_authenticated = True
            return True
        return False

    def check_rbac(self, username, required_role):
        user = self.users.get(username)
        if user and required_role in user.roles and user.is_authenticated:
            return True
        return False

    def encrypt_data(self, data):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = data + b' ' * (16 - len(data) % 16)
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ct

    def decrypt_data(self, encrypted_data):
        iv = encrypted_data[:16]
        ct = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ct) + decryptor.finalize()
        return padded_data.rstrip(b' ')

    def enable_tls(self):
        self.tls_enabled = True

    def is_tls_enabled(self):
        return self.tls_enabled

@pytest.fixture
def system():
    sys = System()
    admin = User('admin', ['admin', 'user'], mfa_enabled=True)
    user = User('user1', ['user'], mfa_enabled=False)
    sys.add_user(admin)
    sys.add_user(user)
    yield sys

def test_rbac_positive(system):
    system.authenticate('admin', 'correct_password', mfa_token='valid_token')
    assert system.check_rbac('admin', 'admin') is True

def test_rbac_negative_wrong_role(system):
    system.authenticate('user1', 'correct_password')
    assert system.check_rbac('user1', 'admin') is False

def test_rbac_negative_not_authenticated(system):
    assert system.check_rbac('admin', 'admin') is False

def test_mfa_positive(system):
    assert system.authenticate('admin', 'correct_password', mfa_token='valid_token') is True

def test_mfa_negative_missing_token(system):
    assert system.authenticate('admin', 'correct_password') is False

def test_mfa_negative_wrong_token(system):
    assert system.authenticate('admin', 'correct_password', mfa_token='invalid_token') is False

def test_mfa_not_required_for_user(system):
    assert system.authenticate('user1', 'correct_password') is True

def test_encryption_decryption_aes256(system):
    data = b'sensitive data'
    encrypted = system.encrypt_data(data)
    assert encrypted != data
    decrypted = system.decrypt_data(encrypted)
    assert decrypted == data

def test_encryption_with_wrong_key(system):
    data = b'sensitive data'
    encrypted = system.encrypt_data(data)
    original_key = system.encryption_key
    system.encryption_key = os.urandom(32)
    with pytest.raises(Exception):
        system.decrypt_data(encrypted)
    system.encryption_key = original_key

def test_encryption_with_short_key(system):
    data = b'sensitive data'
    system.encryption_key = os.urandom(16)
    with pytest.raises(ValueError):
        system.encrypt_data(data)

def test_tls_positive(system):
    system.enable_tls()
    assert system.is_tls_enabled() is True

def test_tls_negative(system):
    assert system.is_tls_enabled() is False
