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
    # Test for no bookmarks
    def test_no_bookmarks(self):
        rv = self.app.get('/bookmarks')
        self.assertIn(b'{\n  "bookmarks": []\n}\n', rv.data)

    # Test to create bookmark
    def test_add_bookmark(self):
        # Create a new user
        rv = self.create_user('Brandon', 'byanofsky@me.com')
        user = json.loads(rv.data.decode())['user']
        user_id = user['id']
        # Create a bookmark that does not follow redirects
        url = 'http://www.google.com'
        rv = self.create_bookmark(url, user_id)
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            ('"url": "{}/"').format(url).encode(),
            rv.data,
            'Bookmark not created properly'
        )

    # Test to create bookmarks that follow redirects
    def test_add_bookmark_follow_redirects(self):
        # Create a new user
        rv = self.create_user('Brandon', 'byanofsky@me.com')
        user = json.loads(rv.data.decode())['user']
        user_id = user['id']
        # Create a bookmark that should follow redirects
        url = 'http://google.com'
        rv = self.create_bookmark(url, user_id, follow_redirects='True')
        self.assertEqual(rv.status_code, 201)
        self.assertIn(
            ('"url": "http://www.google.com/"').format(url).encode(),
            rv.data,
            'Bookmark (follow_redirects) not created properly'
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
