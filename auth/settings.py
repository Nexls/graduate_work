import os

from Cryptodome.PublicKey import RSA

access_token_expires = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 600)
refresh_token_expires = os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 60 * 60 * 24 * 5)

SECRET_KEY = RSA.generate(1024)
private_key = os.environ.get('PRIVATE_KEY', SECRET_KEY.export_key(format='PEM'))
public_key = os.environ.get('PUBLIC_KEY', SECRET_KEY.public_key().export_key(format='PEM'))

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)
REDIS_PASS = os.environ.get('REDIS_PASSWORD', '')

WEB_list = os.environ.get('WEB_LIST', 'macos,linux,windows').split(',')
MOB_list = os.environ.get('MOB_LIST', 'iphone,android').split(',')

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'auth')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'
)

VK_CLIENT_ID = os.environ.get('VK_CLIENT_ID', 7833287)
VK_CLIENT_SECRET = os.environ.get('VK_CLIENT_SECRET', 'c9g48gnuvsZpjEYubZE0')
FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_CLIENT_ID', 871694263408277)
FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_CLIENT_SECRET', 'e88c8aa32ad1533179a85e8ba0b00cb6')

RECAPTCHA_SITE_KEY = '6Lcp3bQaAAAAAJGB-rKIjyrAl0jInGh44dyAz4mm'
RECAPTCHA_SECRET_KEY = '6Lcp3bQaAAAAAPeBTPF3Ah6vKYVCE0zXSpfOSQ-7'
