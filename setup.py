from setuptools import setup

setup(
    name='bookmarks-service',
    packages=['bookmarks-service'],
    version='0.0.1',
    description='A bookmarking and link shortening web service.',
    author='Brandon Yanofsky',
    author_email='byanofsky@me.com',
    include_package_data=True,
    install_requires=[
        'Flask',
        'SQLalchemy',
        'psycopg2',
        'Flask-Bcrypt',
        'Flask-Login',
        'Flask-WTF',
        'requests'
    ],
)
