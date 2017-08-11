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
    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'Good' in rv.data


if __name__ == '__main__':
    # Make sure we are in testing environment, then switch back
    cur_app_env = os.environ.get('APPLICATION_ENVIRONMENT')
    os.environ['APPLICATION_ENVIRONMENT'] = 'testing'
    unittest.main()
    os.environ['APPLICATION_ENVIRONMENT'] = cur_app_env
