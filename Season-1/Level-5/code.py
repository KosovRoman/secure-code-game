# Welcome to Secure Code Game Season-1/Level-5!

# This is the last level of our first season, good luck!

import secrets
import os
import bcrypt

class Random_generator:

    # generates a random token
    def generate_token(self, length=32, alphabet=(
    '0123456789'
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )):
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    # generates salt
    def generate_salt(self, rounds=12):
        return bcrypt.gensalt(rounds=rounds)

class SHA256_hasher:

    MAX_PASSWORD_BYTES = 72

    def _encode(self, password):
        data = password.encode('utf-8')
        if len(data) > self.MAX_PASSWORD_BYTES:
            raise ValueError("password is too long")
        return data

    def password_hash(self, password, salt):
        password_hash = bcrypt.hashpw(self._encode(password), salt)
        return password_hash.decode('ascii')

    # verifies the password against the stored bcrypt hash (constant-time inside bcrypt)
    def password_verification(self, password, password_hash):
        return bcrypt.checkpw(self._encode(password), password_hash.encode('ascii'))

class MD5_hasher:

    def password_hash(self, password):
        return SHA256_hasher().password_hash(password, bcrypt.gensalt())

    def password_verification(self, password, password_hash):
        return SHA256_hasher().password_verification(password, password_hash)

# a collection of sensitive secrets necessary for the software to operate
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')
PASSWORD_HASHER = 'SHA256_hasher'


# Contribute new levels to the game in 3 simple steps!
# Read our Contribution Guideline at github.com/skills/secure-code-game/blob/main/CONTRIBUTING.md
