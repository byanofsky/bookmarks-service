from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('bookmarks_service.default_settings')
app.config.from_pyfile('settings.py', silent=True)

import bookmarks_service.views
