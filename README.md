# bookmarks-service

A bookmarking and link shortening web service with REST API endpoints.

## What It Does

See working example here: https://bookmarks-service.herokuapp.com.

Allows users to save URLs to bookmark IDs (unique, random 6 character alphanumeric sequence). Users can access the saved URL by making a request to the saved bookmark's endpoint.

For instance, making a POST request to `/bookmarks`, passing the `url: 'http://google.com'` in the form data, will yield a bookmark ID (for instance, `"id": "yw6i08"`).

Then, use the returned bookmark `id`, to make a GET request to `/bookmarks/yw6i08`. The response will be:
```
{
    "bookmark": {
        "id": "yw6i08",
        "url": "http://www.google.com/",
        "user_id": 1
    }
}
```

## Getting Started (After Installation)

Looking for installation instructions? [Skip to the installation section](#installation), then come back here.

Looking for API documentation? [Find them here](/API.md).

### Basic Usage

The overall process for working with this web service requires creating a SuperUser, who can create Users. A User can create multiple API Keys. API Keys can be used to create and access bookmarks.

I'll walk you through creating a SuperUser here. All other functionality can be viewed in the [API documentation](/API.md)

### Creating a SuperUser

Because SuperUsers have a lot of power and won't need to be created too often, creating one is intentionally unintuitive.

To create a SuperUser, run this Python code:

```
>>> from bookmarks_service.database import db_session
>>> from bookmarks_service.models import SuperUser
>>> su = SuperUser('password')  # Add your own password here
>>> db_session.add(su)
>>> db_session.commit()
```

You will need to save your password for later use. The SuperUser ID is a sequential integer, so your first SuperUser will have an ID of 1, the second will be 2, and so on.

With the SuperUser created, you can now create Users and Bookmarks. Instructions for these can be found in the [API documentation](/API.md)

## Installation

These instructions will get the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project to a live system.

### Prerequisites

Included in this repo is a Vagrantfile which already has Python 3, virtualenv, and PostgreSQL installed. If you use your own, please see other prerequisites below.

You will need to have [Python 3](https://wiki.python.org/moin/BeginnersGuide/Download) installed, as well as pip, setuptools, and wheels. You most likely already have these 3 installed, but if not, you can find [instructions for installing them here](https://packaging.python.org/tutorials/installing-packages/#install-pip-setuptools-and-wheel).

I'd also recommend setting up a virtual environment using [virtualenv](https://packaging.python.org/tutorials/installing-packages/#optionally-create-a-virtual-environment).

Lastly, you will need a PostgreSQL database set up with a user that has access to that database.

### Installing

Note: If you are using the included Vagrantfile, the application is installed at `/var/www/bookmarks_service/` by default.

1. Create a new directory `/instance/` that should live at the root of your application. This contains instance specific code, so is not version controlled by default.

2. Duplicate `/bookmarks_service/default_settings.py` to `/instance/settings.py`.

3. Update `settings.py` with your own settings. These settings are marked with `TODO` and detailed below.

4. Change the 'USER_AGENT_NAME' to that of your application. This, along with the `VERSION_NUMBER` combine to create your User Agent when the application makes requests to external URLs.

5. Change the `DATABASE_URI` for each environment's database. It should follow the basic structure of:
    ```
    'postgresql://username:password@host/db_name'
    ```

6. Change your `SECRET_KEY`. The recommended way to generate a secret key is to run this code in Python:  
    ```
    >>> import os
    >>> os.urandom(24)
    '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
    ```

7. Set your environment variables:
    ```
    export FLASK_APP=bookmarks_service
    export FLASK_DEBUG=1
    export APPLICATION_ENVIRONMENT='development'
    ```
The `APPLICATION_ENVIRONMENT` needs to match with your current environment: `'production'`, `'development'`, or `'testing'`. If none is set, `'development'` is used by default.

8. Create database schema by running in python:
    ```
    >>> from bookmarks_service import init_db
    >>> init_db()
    ```
If you are using multiple application environments, you will need to change your `APPLICATION_ENVIRONMENT` variable and run this for each database.

9. Start the Flask development server with:
    ```
    flask run
    ```
If you are running on a Vagrant machine, you will need to append ` -h 0.0.0.0` to run so it is publicly accessible. [More info here](http://flask.pocoo.org/docs/0.12/quickstart/#public-server).

You can now access the application via the default URL `localhost:5000`.

## Running Tests

I've included a basic test suite that is used to test all functionality. It uses the Python unittest library.

You must set '`APPLICATION_ENVIRONMENT`' to `'testing'` for the tests to run, or the test suite won't run. The tests will clear the database after each test, so this check is to protect dev and production databases.

To run the tests, from the root of the application, run:
```
python tests/test_bookmarks.py
```

If a test fails, it will specify which test.

## Deployment

Coming Soon!

## TODO

* Improve test suite so it is easier to understand which tests fail
* Include editing and deleting routes for users and bookmarks
* Move documentation to a wiki, because this is getting long

## Built With

* [Flask](http://flask.pocoo.org/) - web framework
* [SQLalchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
* [psycopg2](http://initd.org/psycopg/) - PostgreSQL adapter for Python
* [Requests](http://docs.python-requests.org/en/master/) - HTTP library for Python
* [bcrypt](https://pypi.python.org/pypi/bcrypt/3.1.0) - Password hashing library for Python

## Authors

- [Brandon Yanofsky](https://github.com/byanofsky)

## License

Copyright 2017 Brandon Yanofsky

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
