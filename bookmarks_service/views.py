import random
import re
import string
from functools import wraps

from flask import g, abort, jsonify, make_response, request
import requests
import bcrypt

from bookmarks_service import app
from bookmarks_service.database import db_session
from bookmarks_service.models import User, Bookmark, Request, API_Key

# Create user agent for requests
USER_AGENT = '{}/{}'.format(
    app.config['USER_AGENT_NAME'],
    app.config['VERSION_NUMBER'])
# Timeout for requests library
TIMEOUT = app.config['TIMEOUT']


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth = request.authorization
            user_id = request.authorization['username']
            password = request.authorization['password']
        # Catches exception if there is no authorization header or not
        # formatted as basic authorization
        except TypeError as e:
            return jsonify(
                error='Unauthorized', code='401',
                message='You must include a proper authorization header'
            ), 401
        # Catches exception if authorization header does not include username
        # and password
        except KeyError as e:
            return jsonify(
                error='Unauthorized', code='401',
                message='You must include a username and password'
            ), 401
        user = User.query.get(user_id)
        # Check that secret matches api_key secret
        if not bcrypt.checkpw(password.encode('utf-8'),
                              user.password_hash.encode('utf-8')):
            return jsonify(
                error='Unauthorized', code='401',
                message='You must be authenticated to access'
            ), 401
        # Store user
        g.user = user
        # Continue with function
        return f(*args, **kwargs)
    return decorated_function


def is_authorized(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        assert 'user_id' in kwargs
        user_id = int(kwargs['user_id'])
        if not g.user or g.user.id != user_id:
            return jsonify(
                error='Unauthorized', code='401',
                message='You are not authorized to access this route'
            ), 401
        return f(*args, **kwargs)
    return decorated_function


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth = request.authorization
            api_key_id = request.authorization['username']
            secret = request.authorization['password']
        # Catches exception if there is no authorization header or not
        # formatted as basic authorization
        except TypeError as e:
            return jsonify(
                error='Unauthorized', code='401',
                message='You must include a proper authorization header'
            ), 401
        # Catches exception if authorization header does not include username
        # and password
        except KeyError as e:
            return jsonify(
                error='Unauthorized', code='401',
                message='You must include a username and password'
            ), 401
        api_key = API_Key.query.get(api_key_id)
        # Check that secret matches api_key secret
        if api_key.secret != secret:
            return jsonify(
                error='Unauthorized', code='401',
                message='You must be authenticated to access'
            ), 401
        # Store user and api key
        g.api_key = api_key
        g.user = api_key.user
        # Continue with function
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
def front_page():
    return (
        'Welcome to the bookmarks web service API. \n'
        'With this API, you can create store URLs in a (somewhat) '
        'shortened version.\n'
        'To create an account, make a POST request to "/users", passing '
        '"name" and "email".\n'
        'The response will include a "user_id". Save this.\n'
        'To create a bookmark, make a POST request to "/bookmarks", passing '
        'a "url" and "user_id". If you want to follow redirects, include the '
        'key "follow_redirects" with the value "True".\n'
        'The response will include an id, which you can use to access this '
        'url. Just make a GET request to "bookmarks/\{id\}", where \{id\} '
        'is the bookmark id you want to retrieve.'
    )


@app.route('/bookmarks', methods=['GET', 'POST'])
@auth_required
def bookmarks():
    if request.method == 'POST':
        # Get data
        url = request.form.get('url')
        follow_redirects = request.form.get('follow_redirects') == 'True'
        # Verify required data sent
        if not (url):
            msg = 'url is required: (url={})'.format(
                url
            )
            return (jsonify(
                error='Bad Request',
                code='400',
                message=msg
            ), 400)
        # Verify URL
        try:
            user_agent = '{}/{}'.format(
                app.config['USER_AGENT_NAME'],
                app.config['VERSION_NUMBER']
            )
            r = requests.get(
                url,
                headers={'user-agent': user_agent},
                allow_redirects=follow_redirects,
                timeout=app.config['TIMEOUT']
            )
            r.raise_for_status()
        # Catch request exceptions
        except requests.exceptions.RequestException as e:
            # Customize error message to request exception
            if isinstance(e, requests.exceptions.HTTPError):
                msg = str(e)
            elif isinstance(e, requests.exceptions.Timeout):
                msg = ('Timeout error. Please try again. If error continues, '
                       'please check that submitted url is correct.')
            elif isinstance(e, requests.exceptions.ConnectionError):
                msg = ('Could not connect to your url. '
                       'Please check that url is correct. ' + str(e))
            elif isinstance(e, requests.exceptions.TooManyRedirects):
                msg = ('Exceeded max number of redirects when connecting to '
                       'url. Please check URL.')
            else:
                msg = str(e)
            return (jsonify(
                error='Bad Request',
                code='400',
                message='Error when connecting to submitted url: ' + msg
            ), 400)
        else:
            # If url success, get final url (important for redirects)
            url = r.url
        # Successfully verified, time to create bookmark.
        # Generate random 6 character alphanumeric id
        while True:
            b_id = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(6))
            # Check that id does not exist
            if Bookmark.query.get(b_id) is None:
                break
        # Create bookmark in database
        b = Bookmark(b_id, url, user_id=g.user.id)
        db_session.add(b)
        db_session.commit()
        # Craft response
        response = make_response(
            jsonify(
                bookmark=b.json()
            )
        )
        # Provide location of user resource
        response.headers['Location'] = '/bookmarks/{}'.format(b.id)
        return response, 201
    # Get all bookmarks
    bookmarks = Bookmark.query.all()
    return jsonify(bookmarks=[b.json() for b in bookmarks])


@app.route('/bookmarks/<bookmark_id>', methods=['GET'])
def single_bookmark(bookmark_id):
    # Verify bookmark id
    if not re.fullmatch('^[0-9a-z]{6}$', bookmark_id):
        return (jsonify(
            error='Bad Request',
            code='400',
            message='Bookmark id must be 6 alphanumeric characters'
        ), 400)
    # Query bookmark
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark:
        return (jsonify(
            error='Not Found',
            code='404',
            message='There is not bookmark with the id={}'.format(bookmark_id)
        ), 404)
    return jsonify(bookmark=bookmark.json())


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        # Get data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        # Verify data sent
        if not (name and password and email):
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
        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode('utf-8')
        u = User(name, email, password_hash)
        db_session.add(u)
        db_session.commit()
        # Craft response
        response = make_response(
            jsonify(
                user=u.json()
            )
        )
        # Provide location of user resource
        response.headers['Location'] = '/users/{}'.format(u.id)
        return response, 201
    # Query users and return
    users = User.query.all()
    return jsonify(users=[u.json() for u in users])


@app.route('/users/<user_id>', methods=['GET'])
@login_required
@is_authorized
def single_user(user_id):
    # Query users
    user = User.query.get(user_id)
    if not user:
        return (jsonify(
            error='Not Found',
            code='404',
            message='There is not a user with the id={}'.format(user_id)
        ), 404)
    return jsonify(user=user.json())


@app.route('/api_keys', methods=['GET', 'POST'])
@login_required
def api_keys():
    if request.method == 'POST':
        # Create api key in database
        # Generate random 24 character alphanumeric id
        while True:
            k_id = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(24))
            # Check that id does not exist
            if API_Key.query.get(k_id) is None:
                break
        secret = ''.join(random.choice(
            string.ascii_lowercase + string.digits) for _ in range(60))
        k = API_Key(id=k_id, secret=secret, user_id=g.user.id)
        db_session.add(k)
        db_session.commit()
        # Craft response
        response = make_response(
            jsonify(
                api_key=k.json()
            )
        )
        return response, 201
    # Query api keys and return
    api_keys = API_Key.query.filter_by(user_id=g.user.id).all()
    return jsonify(api_keys=[k.json() for k in api_keys])
