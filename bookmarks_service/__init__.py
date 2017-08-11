from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('bookmarks_service.default_settings')
app.config.from_pyfile('settings.py', silent=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

import bookmarks_service.views
