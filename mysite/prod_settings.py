# Import all default settings.
from .settings import *
STATIC_ROOT = 'staticfiles'
ALLOWED_HOSTS=["*"]
DEBUG=False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')