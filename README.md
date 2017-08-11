# bookmarks-service

A bookmarking and link shortening web service with REST API endpoints.

## What It Does

Allows users to save URLs to shortened link IDs.

Each ID is a 6 character, alphanumeric sequence. Users can access the saved URL by making a request to the API and passing this ID.

Requests made to access a saved URL are tracked so that a user can see how many times a link was requested and by which IP addresses.

## Getting Started

These instructions will get the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project to a live system.

### Prerequisites

Coming Soon!

### Installing

Coming Soon!

## Running Tests

Coming Soon!

## Deployment

Coming Soon!

## Built With

* [Flask](http://flask.pocoo.org/) - web framework
* [SQLalchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
* [psycopg2](http://initd.org/psycopg/) - PostgreSQL adapter for Python
* [Flask-Bcrypt](https://flask-bcrypt.readthedocs.io/en/latest/) - Flask extension that provides bcrypt hashing utilities
* [Flask-Login](https://flask-login.readthedocs.io/en/latest/) - Flask extension that provides user session management
* [WTForms](https://wtforms.readthedocs.io/en/latest/) - forms validation and rendering library for Python
* [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) - Flask extension that integrates WTForms
'requests'

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
