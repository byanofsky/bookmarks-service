import os
import re
import unittest

import bookmarks_service


class BookmarksTestCase(unittest.TestCase):
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

    # Begin test functions
    def test_front_page(self):
        rv = self.app.get('/')
        self.assertIn(b'Welcome to the bookmarks web service API.', rv.data)

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

    # Test for no bookmarks
    def test_no_bookmarks(self):
        rv = self.app.get('/bookmarks')
        self.assertIn(b'{\n  "bookmarks": []\n}\n', rv.data)


if __name__ == '__main__':
    # Make sure we are in testing mode and testing env
    app_env = os.environ.get('APPLICATION_ENVIRONMENT')
    if (bookmarks_service.app.config['TESTING'] is True and
            app_env == 'testing'):
            unittest.main()
    else:
        print('Need to be in a testing environment. ' +
              'Set APPLICATION_ENVIRONMENT to testing.')
