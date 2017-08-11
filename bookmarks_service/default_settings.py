import os
import pkg_resources  # part of setuptools

# Get environment, or set to development by default
app_env = os.environ.get('APPLICATION_ENVIRONMENT') or 'development'

# User agent name for requests
USER_AGENT_NAME = 'bookmarks_service'  # TODO: Enter user agent name
# Version number taken from setup.py
VERSION_NUMBER = pkg_resources.require('bookmarks_service')[0].version
# Flask secret key. See README for more info
SECRET_KEY = 'development key'  # TODO: Enter secret key
# Prevents test from running by default
TESTING = False
# Request timeout limit, in seconds
TIMEOUT = 5

if app_env == 'production':
    DATABASE_URI = ''  # TODO: Enter your production database
    DEBUG = False

if app_env == 'development':
    DATABASE_URI = ''  # TODO: Enter your dev database
    DEBUG = True

if app_env == 'testing':
    DATABASE_URI = ''  # TODO: Enter your test database
    TESTING = True  # Allows testing to run
    TIMEOUT = 1  # Sets timeout to 1 second for testing
