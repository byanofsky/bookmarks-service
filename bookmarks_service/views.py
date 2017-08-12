from flask import abort, jsonify, make_response, request

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
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        # Get data
        name = request.form.get('name')
        email = request.form.get('email')
        # Verify data sent
        if not (name and email):
            return (jsonify(
                error='Bad Request',
                code='400',
                message='Please check request data'
            ), 400)
        # Check if user exists with email address
        if User.query.filter(User.email == email).one_or_none():
            return (jsonify(
                error='Conflict',
                code='409',
                message='A user with this email already exists'
            ), 409)
        # Create user in database
        u = User(name=name, email=email)
        db_session.add(u)
        db_session.commit()
        # Craft response
        response = make_response(
            jsonify(
                user=u.json()
            )
        )
        response.headers['Location'] = '/users/{}'.format(u.id)
        return response, 201
    # Query users and return
    users = User.query.all()
    return jsonify(users=[u.json() for u in users])
