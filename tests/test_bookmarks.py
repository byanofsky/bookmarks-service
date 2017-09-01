import os
import re
import unittest
import json

import bookmarks_service


class BaseTestCase(unittest.TestCase):
    # Setup and teardown functions
    def setUp(self):
        self.app = bookmarks_service.app.test_client()
        bookmarks_service.database.init_db()

    def tearDown(self):
        bookmarks_service.database.db_session.remove()
        bookmarks_service.database.Base.metadata.drop_all(
            bind=bookmarks_service.database.engine)

    # Helper functions for tests
    def create_user(self, name, email):
        rv = self.app.post('/users', data={
            'name': name,
            'email': email
        })
        return rv

    def create_bookmark(self, url, user_id, follow_redirects=None):
        data = {
            'url': url,
            'user_id': user_id
        }
        if follow_redirects:
            data['follow_redirects'] = follow_redirects
        rv = self.app.post('/bookmarks', data=data)
        return rv


class GeneralTestCase(BaseTestCase):
    def test_front_page(self):
        rv = self.app.get('/')
        self.assertIn(b'Welcome to the bookmarks web service API.', rv.data)


class UsersTestCase(BaseTestCase):
    # Test for no users
    def test_no_users(self):
        rv = self.app.get('/users')
        self.assertIn(b'{\n  "users": []\n}\n', rv.data)

    # Test creating a new user
    def test_create_user(self):
        # Create user
        rv = self.create_user('Brandon Yanofsky', 'byanofsky@me.com')
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            b'"email": "byanofsky@me.com",',
            rv.data,
            'User not successfully created'
        )

    # Test attempt to create user without passing data
    def test_create_user_no_data(self):
        # Attempt to create a user without passing data
        rv = self.app.post('/users')
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'"error": "Bad Request"',
            rv.data,
            'User post request without data should return "Bad Request"'
        )

    # Test attempt to create user with email that exists
    def test_create_user_that_exists(self):
        # Create a user
        self.create_user('Brandon Yanofsky', 'byanofsky@me.com')
        # Create user with same email address
        rv = self.create_user('Brandon Yanofsky 2', 'byanofsky@me.com')
        self.assertEqual(rv.status_code, 409)
        self.assertIn(
            b'"error": "Conflict"',
            rv.data,
            'Adding a user with email that exists should return 409 error'
        )


class BookmarksTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create a new user
        rv = self.create_user('Brandon', 'byanofsky@me.com')
        self.user = json.loads(rv.data.decode())['user']
        self.user_id = self.user['id']

    # Test for no bookmarks
    def test_no_bookmarks(self):
        rv = self.app.get('/bookmarks')
        self.assertIn(b'{\n  "bookmarks": []\n}\n', rv.data)

    # Test to create bookmark
    def test_add_bookmark(self):
        # Create a bookmark that does not follow redirects
        url = 'http://www.google.com'
        rv = self.create_bookmark(url, self.user_id)
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
        rv = self.create_bookmark(url, self.user_id, follow_redirects='True')
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            b'"url": "http://www.google.com/"',
            rv.data,
            'Bookmark (follow_redirects) not created properly'
        )

    # Test add bookmark errors
    def test_add_bookmark_errors(self):
        # Check error when URL & user_id empty
        rv = self.create_bookmark(None, None)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'url and user_id are required:',
            rv.data,
            'Failed test when url and user_id empty'
        )
        # Check error when URL empty
        rv = self.create_bookmark(None, self.user_id)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'url and user_id are required:',
            rv.data,
            'Failed test when url is empty'
        )
        # Check error when user_id empty
        rv = self.create_bookmark('http://google.com', None)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'url and user_id are required:',
            rv.data,
            'Failed test when user_id is empty'
        )
        # Check error when user_id does not exist
        rv = self.create_bookmark('http://google.com', 50)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'No user exists with user_id=50',
            rv.data,
            'Failed test when user does not exist'
        )
        # Check error when url has HTTPError
        rv = self.create_bookmark('http://google.com/testing', self.user_id)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'404 Client Error',
            rv.data,
            'Failed test when url test has HTTPError'
        )
        # Check error when url has Timeout
        rv = self.create_bookmark('http://github.com:81', self.user_id)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(
            b'Timeout error. Please try again.',
            rv.data,
            'Failed test when url test has Timeout'
        )
        # Check error when url has Connection Error
        rv = self.create_bookmark('http://googlecom', self.user_id)
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
            'http://www.google.com',
            self.user_id,
            follow_redirects='True'
        )
        self.assertEqual(rv.status_code, 201, msg='Error creating bookmark')
        # Store returned bookmark location
        b_url = rv.headers['Location']
        # Get bookmark
        rv = self.app.get(b_url)
        bookmark = json.loads(rv.data.decode())['bookmark']
        self.assertEqual(rv.status_code, 200, msg='Error retrieving bookmark')
        self.assertIn(
            b'"url": "http://www.google.com/"',
            rv.data,
            'Bookmark get failed'
        )

    # Test bookmark retrieval errors
    def test_get_bookmark_errors(self):
        # Use incorrect bookmark id format
        rv = self.app.get('/bookmarks/123')
        self.assertEqual(rv.status_code, 400, msg='Incorrect status code')
        self.assertIn(
            b'Bookmark id must be 6 alphanumeric characters',
            rv.data,
            'Bookmark get error message is not correct'
        )
        # User bookmark id that does not exist
        rv = self.app.get('/bookmarks/a1b2c3')
        self.assertEqual(rv.status_code, 404, msg='Incorrect status code')
        self.assertIn(
            b'There is not bookmark with the id=a1b2c3',
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
