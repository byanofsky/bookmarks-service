from flask import jsonify
from flask import jsonify, request

from bookmarks_service import app
from bookmarks_service.database import db_session
from bookmarks_service.models import User, Bookmark, Request

# Create user agent for requests
USER_AGENT = '{}/{}'.format(
    app.config['USER_AGENT_NAME'],
    app.config['VERSION_NUMBER'])
# Timeout for requests library
TIMEOUT = app.config['TIMEOUT']


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/', methods=['GET'])
def front_page():
    return (
        'Welcome to the bookmarks web service API. '
        'More info will be added here in the future in case you are lost.'
    )


@app.route('/bookmarks/', methods=['GET'])
def _bookmarks():
    # Get all bookmarks
    bookmarks = Bookmark.query.all()
    if not bookmarks:
        return jsonify(bookmarks=[])
    return 'Something soon'
@app.route('/users/', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        # Query users and return
        users = User.query.all()
        return jsonify(users=users)
    return 'Next steps'
