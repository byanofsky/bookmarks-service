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

    # Begin test functions
    def test_front_page(self):
        rv = self.app.get('/')
        self.assertIn(b'Welcome to the bookmarks web service API.', rv.data)

    # Test for no bookmarks
    def test_no_bookmarks(self):
        rv = self.app.get('/bookmarks/')
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
