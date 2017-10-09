import os
import re
import unittest
import json
import base64

import bookmarks_service
from bookmarks_service.models import SuperUser


class BaseTestCase(unittest.TestCase):
    # Setup and teardown functions
    def setUp(self):
        self.app = bookmarks_service.app.test_client()
        bookmarks_service.database.init_db()

        self.create_super_user('12345')

    def tearDown(self):
        bookmarks_service.database.db_session.remove()
        bookmarks_service.database.Base.metadata.drop_all(
            bind=bookmarks_service.database.engine)

    # Helper functions for tests
    def create_user(self, name, email, password):
        rv = self.app.post(
            '/users',
            data={
                'name': name,
                'email': email,
                'password': password
            },
            headers=self.super_user_headers
        )
        return rv

    def create_super_user(self, password):
        # Create a super user and create a super user auth header
        superuser = SuperUser(password)
        bookmarks_service.database.db_session.add(superuser)
        bookmarks_service.database.db_session.commit()
        auth_value = "{}:{}".format(1, '12345')
        auth = base64.b64encode(auth_value.encode())
        header = {'Authorization': b'Basic ' + auth}
        self.super_user_headers = header

    def create_bookmark(self, url, follow_redirects=None, headers=None):
        if not headers:
            headers = self.headers
        data = {
            'url': url
        }
        if follow_redirects:
            data['follow_redirects'] = follow_redirects
        rv = self.app.post('/bookmarks', data=data, headers=headers)
        return rv

    def create_api_key(self, headers):
        rv = self.app.post('/api_keys', headers=headers)
        return rv


class GeneralTestCase(BaseTestCase):
    def test_front_page(self):
        rv = self.app.get('/')
        # self.assertIn(b'Welcome to the bookmarks web service API.', rv.data)
        self.assertEqual(rv.status_code, 200)


class SuperAdminTestCase(BaseTestCase):
    # Test for super user authorization
    def test_bookmark_auth_required(self):
        # Test GET without authorization
        rv = self.app.get('/users')
        self.assertEqual(rv.status_code, 401)
        # Test POST without authorization
        rv = self.app.post('/users')
        self.assertEqual(rv.status_code, 401)

    # Test for no users
    def test_no_users(self):
        rv = self.app.get('/users', headers=self.super_user_headers)
        self.assertIn(b'{\n  "users": []\n}\n', rv.data)

    # Test creating a new user
    def test_create_user(self):
        # Create user
        rv = self.create_user(
            'John Smith',
            'jsmith22@me.com',
            '64John!Smith45'
        )
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            b'"email": "jsmith22@me.com",',
            rv.data,
            'User not successfully created'
        )

    # Test attempt to create user without passing data
    def test_create_user_no_data(self):
        # Attempt to create a user without passing data
        rv = self.app.post('/users', headers=self.super_user_headers)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'"error": "Bad Request"',
            rv.data,
            'User post request without data should return "Bad Request"'
        )

        # Test attempt to create user with email that exists
        def test_create_user_that_exists(self):
            # Create a user
            self.create_user(
                'John Smith',
                'jsmith22@me.com',
                '64John!Smith45'
            )
            # Create user with same email address
            rv = self.create_user(
                'Joseph A Smith',
                'jsmith22@me.com',
                'Joe!Smith22'
            )
            self.assertEqual(rv.status_code, 409)
            self.assertIn(
                b'"error": "Conflict"',
                rv.data,
                'Adding a user with email that exists should return 409 error'
            )

        # Test add and get user
        def test_add_and_get_user(self):
            # Create user
            rv = self.create_user(
                'John Smith',
                'jsmith22@me.com',
                '64John!Smith45'
            )
            self.assertEqual(rv.status_code, 201, msg='Error creating user')
            # Store returned user location
            u_url = rv.headers['Location']
            # Get user
            rv = self.app.get(u_url)
            bookmark = json.loads(rv.data.decode())['user']
            self.assertEqual(rv.status_code, 200, msg='Error retrieving user')
            self.assertIn(
                b'"email": "jsmith22@me.com"',
                rv.data,
                'User get failed'
            )

        # Test user retrieval errors
        def test_get_user_errors(self):
            # User id that does not exist
            rv = self.app.get('/users/25')
            self.assertEqual(rv.status_code, 404, msg='Incorrect status code')
            self.assertIn(
                b'There is not a user with the id=25',
                rv.data,
                'User get error message is not correct'
            )


class APIKeyTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a new user
        user_pw = '22John!Smith44'
        rv = self.create_user(
            'John Smith',
            'jsmith22@me.com',
            user_pw
        )
        self.user = json.loads(rv.data.decode())['user']
        self.user_id = self.user['id']
        self.user_pw = user_pw

        auth_value = "{}:{}".format(self.user_id, self.user_pw)
        auth = base64.b64encode(auth_value.encode())
        self.headers = {'Authorization': b'Basic ' + auth}

    # Test api key authentication
    def test_api_key_login_required(self):
        # Test GET without authorization
        rv = self.app.get('/api_keys')
        self.assertEqual(rv.status_code, 401)
        # Test POST without authorization
        rv = self.app.post('/api_keys')
        self.assertEqual(rv.status_code, 401)

        # Create authorization headers with wrong password
        auth_value = "{}:{}".format(self.user_id, 'password')
        auth = base64.b64encode(auth_value.encode())
        headers_wrong_pw = {'Authorization': b'Basic ' + auth}
        # Test GET with wrong password
        rv = self.app.get(
            '/api_keys',
            headers=headers_wrong_pw
        )
        self.assertEqual(rv.status_code, 401)
        # Test POST with wrong password
        rv = self.app.post(
            '/api_keys',
            headers=headers_wrong_pw
        )
        self.assertEqual(rv.status_code, 401)

        # Create authorization headers with wrong format
        headers_wrong_format = {'Authorization': ':'}
        # Test GET with wrong format auth header
        rv = self.app.get(
            '/api_keys',
            headers=headers_wrong_format
        )
        self.assertEqual(rv.status_code, 401)
        # Test POST with wrong format auth header
        rv = self.app.post(
            '/api_keys',
            headers=headers_wrong_format
        )
        self.assertEqual(rv.status_code, 401)

    # Test for no api keys
    def test_no_api_keys(self):
        rv = self.app.get(
            '/api_keys',
            headers=self.headers)
        self.assertIn(b'{\n  "api_keys": []\n}\n', rv.data)

    # Test creating an API Key
    def test_create_api_key(self):
        rv = self.create_api_key(headers=self.headers)
        self.assertEqual(rv.status_code, 201)
        api_key = json.loads(rv.data.decode())['api_key']

    # Test adding a few API keys, but only view API Keys created by user
    def test_multiple_api_keys(self):
        # Create 4 API Keys with one user
        for _ in range(4):
            self.create_api_key(headers=self.headers)
        # Check that there are 4 api keys
        rv = self.app.get(
            '/api_keys',
            headers=self.headers
        )
        api_keys_1 = json.loads(rv.data.decode())['api_keys']
        self.assertEqual(len(api_keys_1), 4)
        # Create 2nd user
        self.create_user(
            'Alex Frank',
            'afrank500@me.com',
            '123Password!'
        )
        # 2nd user header
        auth_value = "{}:{}".format(2, '123Password!')
        auth = base64.b64encode(auth_value.encode())
        header = {'Authorization': b'Basic ' + auth}
        # Create 2 api keys for user
        for _ in range(2):
            self.create_api_key(headers=header)
        # Check that there are 2 api keys
        rv = self.app.get(
            '/api_keys',
            headers=header
        )
        api_keys_2 = json.loads(rv.data.decode())['api_keys']
        self.assertEqual(len(api_keys_2), 2)


class BookmarksTestCase(BaseTestCase):
    # TODO: Fix these up a bit. messy.
    def setUp(self):
        super().setUp()
        # Create a new user
        password = '22John!Smith44'
        rv = self.create_user(
            'John Smith',
            'jsmith22@me.com',
            password
        )
        # Store user ID for later
        user_id = json.loads(rv.data.decode())['user']['id']
        # Create a user authorization header
        user_auth_value = "{}:{}".format(user_id, password)
        user_auth = base64.b64encode(user_auth_value.encode())
        user_headers = {'Authorization': b'Basic ' + user_auth}
        # Create and store new API Key
        rv = self.create_api_key(headers=user_headers)
        self.api_key = json.loads(rv.data.decode())['api_key']['id']
        self.secret = json.loads(rv.data.decode())['api_key']['secret']
        # Create an authorization header using API Key and Secret
        auth_value = "{}:{}".format(self.api_key, self.secret)
        auth = base64.b64encode(auth_value.encode())
        # Store authorization header to instance
        self.headers = {'Authorization': b'Basic ' + auth}

    # Test for authorization when accessing bookmarks
    def test_bookmark_auth_required(self):
        # Test GET without authorization
        rv = self.app.get('/bookmarks')
        self.assertEqual(rv.status_code, 401)
        # Test POST without authorization
        rv = self.app.post('/bookmarks')
        self.assertEqual(rv.status_code, 401)

        # Create authorization header with invalid API Key
        api_key = '12345'
        secret = 'Secret'
        # Create an authorization header using API Key and Secret
        invalid_auth_value = "{}:{}".format(api_key, secret)
        invalid_auth = base64.b64encode(invalid_auth_value.encode())
        invalid_headers = {'Authorization': b'Basic ' + invalid_auth}
        # Test GET with invalid API Key
        rv = self.app.get(
            '/bookmarks',
            headers=invalid_headers
        )
        self.assertEqual(rv.status_code, 401)
        # Test POST with wrong password
        rv = self.app.post(
            '/bookmarks',
            headers=invalid_headers
        )
        self.assertEqual(rv.status_code, 401)

        # Create authorization header with invalid Secret
        api_key = self.api_key
        secret = 'Secret'
        # Create an authorization header using API Key and Secret
        invalid_auth_value = "{}:{}".format(api_key, secret)
        invalid_auth = base64.b64encode(invalid_auth_value.encode())
        invalid_headers = {'Authorization': b'Basic ' + invalid_auth}
        # Test GET with invalid API Key
        rv = self.app.get(
            '/bookmarks',
            headers=invalid_headers
        )
        self.assertEqual(rv.status_code, 401)
        # Test POST with wrong password
        rv = self.app.post(
            '/bookmarks',
            headers=invalid_headers
        )
        self.assertEqual(rv.status_code, 401)

    # Test for no bookmarks
    def test_no_bookmarks(self):
        rv = self.app.get(
            '/bookmarks',
            headers=self.headers)
        self.assertIn(b'{\n  "bookmarks": []\n}\n', rv.data)

    # Test to create bookmark
    def test_add_bookmark(self):
        # Create a bookmark that does not follow redirects
        url = 'http://www.google.com'
        rv = self.create_bookmark(url)
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            b'"url": "http://www.google.com/"',
            rv.data,
            'Bookmark not created properly'
        )

    # Test to create bookmarks that follow redirects
    def test_add_bookmark_follow_redirects(self):
        # Create a bookmark that should follow redirects
        url = 'http://google.com'
        rv = self.create_bookmark(
            url,
            follow_redirects='True'
        )
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            b'"url": "http://www.google.com/"',
            rv.data,
            'Bookmark (follow_redirects) not created properly'
        )

    # Test add bookmark errors
    def test_add_bookmark_errors(self):
        # Check error when URL empty
        rv = self.create_bookmark(None)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'URL is required',
            rv.data,
            'Failed test when url is empty'
        )
        # Check error when url has HTTPError
        rv = self.create_bookmark('http://google.com/testing')
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'404 Client Error',
            rv.data,
            'Failed test when url test has HTTPError'
        )
        # Check error when url has Timeout
        rv = self.create_bookmark('http://github.com:81')
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'Timeout error. Please try again.',
            rv.data,
            'Failed test when url test has Timeout'
        )
        # Check error when url has Connection Error
        rv = self.create_bookmark('http://googlecom')
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'Could not connect to your url',
            rv.data,
            'Failed test when url test Connection Error'
        )
        # Check error when url has TooManyRedirects
        # TODO: find way to simulate too many redirects error

    # Test add and get bookmark
    def test_add_and_get_bookmark(self):
        # Create bookmark
        rv = self.create_bookmark(
            'http://google.com',
            follow_redirects='True'
        )
        self.assertEqual(rv.status_code, 201, msg='Error creating bookmark')
        # Store returned bookmark location
        b_url = rv.headers['Location']
        # Get bookmark
        rv = self.app.get(b_url, headers=self.headers)
        self.assertEqual(rv.status_code, 200, msg='Error retrieving bookmark')
        bookmark = json.loads(rv.data.decode())['bookmark']
        self.assertEqual(
            bookmark['url'],
            'http://www.google.com/',
            'Bookmark get failed'
        )

    # Test bookmark retrieval errors
    def test_get_bookmark_errors(self):
        # Use incorrect bookmark id format
        rv = self.app.get('/bookmarks/123', headers=self.headers)
        self.assertEqual(rv.status_code, 400, msg='Incorrect status code')
        self.assertIn(
            b'Bookmark id must be 6 alphanumeric characters',
            rv.data,
            'Bookmark get error message is not correct'
        )
        # User bookmark id that does not exist
        rv = self.app.get('/bookmarks/a1b2c3', headers=self.headers)
        self.assertEqual(rv.status_code, 404, msg='Incorrect status code')
        self.assertIn(
            b'There is no bookmark with the id=a1b2c3',
            rv.data,
            'Bookmark get error message is not correct'
        )


if __name__ == '__main__':
    # Make sure we are in testing mode and testing env
    app_env = os.environ.get('APPLICATION_ENVIRONMENT')
    if (bookmarks_service.app.config['TESTING'] is True and
            app_env == 'testing'):
            unittest.main(verbosity=2)
    else:
        print('Need to be in a testing environment. ' +
              'Set APPLICATION_ENVIRONMENT to testing.')
