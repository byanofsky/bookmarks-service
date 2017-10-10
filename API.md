# API Documentation

## Quick Links
* [Authentication](#authentication)
* [Get All Bookmarks](#get-all-bookmarks)
* [Create Bookmark](#create-bookmark)
* [Get Bookmark](#get-bookmark)
* [Get All Users](#get-all-users)
* [Create User](#create-user)
* [Get User](#get-user)
* [Get All API Keys](#get-all-api-keys)
* [Create API Key](#create-api-key)

## Authentication

Authentication is handled via the `Authorization` request header, using a Basic authentication type.

The structure for this header is:

```
Authorization: Basic <credentials>
```

`<credentials>` must be a string with a username and password, separated by a colon (`'Username:Password'`), and that string must be base64 encoded ([more info here](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization)).

The username and password that must be used depends on the type of request. Please see the 'Authentication' section under each type of request below.

## Get All Bookmarks

Retrieve all bookmarks owned by User who owns API Key.

* **URL**: `/bookmarks`
* **Method**: `GET`
* **Authentication**:
  * `username`: API Key ID  
  * `password`: API Key Secret
* **Success Response**:
  * Code: `200`
  * Content:
    ```
    {
      "bookmarks": [
        {
          "id": "123456",
          "url": "http://www.google.com/",
          "user_id": 1
        },
        {
          "id": "abcdef",
          "url": "http://www.github.com/",
          "user_id": 1
        },
        ...
      ]
    }
    ```
* **Error Response**:
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```

## Create Bookmark

Create a new bookmark.

* **URL**: `/bookmarks`
* **Method**: `POST`
* **Authentication**
  * `username`: API Key ID  
  * `password`: API Key Secret  
* **Data Params**
  * **Required**  
    `url=[properly formatted url]`
  * **Optional**  
    `follow_redirects=[True]` : Follow all redirects and save final url
* **Success Response**
  * Code: `201`
  * Content:
    ```
    {
      "bookmark": {
        "id": "123456",
        "url": "http://www.google.com/",
        "user_id": 1
      }
    }
    ```
* **Error Responses**
  * Code: `400`
  * Content:
    ```
    {
      "code": "401",
      "error": "Bad Request",
      "message": "URL is required"
    }
    ```
  OR
  * Code: `400`
  * Content:
    ```
    {
      "code": "401",
      "error": "Bad Request",
      "message": [Error message when requesting external URL]
    }
    ```
  OR
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```

## Get Bookmark

Retrieve a single bookmark.

* **URL**: `/bookmark/:id`  
* **Method**: `GET`
* **Authentication**
  * `username`: API Key ID  
  * `password`: API Key Secret
* **Success Response**
  * Code: `200`
  * Content:
    ```
    {
      "bookmark": {
        "id": "123456",
        "url": "http://www.google.com/",
        "user_id": 1
      }
    }
    ```
* **Error Response**
  * Code: `400`
  * Content:
    ```
    {
      "error": "Bad Request",
      "code": "400",
      "message": "Bookmark id must be 6 alphanumeric characters"
    }
	```
  OR
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```
  OR
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You are not authorized to access this route"
    }
    ```
  OR
  * Code: `404`
  * Content:
    ```
    {
      "error": "Not Found",
      "code": "404",
      "message": "There is no bookmark with the id=abcdef"
    }
    ```

## Get All Users

Retrieve all users.

* **URL**: `/users`  
* **Method**: `GET`
* **Authentication**
  * `username`: SuperUser ID  
  * `password`: SuperUser Password
* **Success Response**
  * Code: `200`
  * Content:
    ```
    {
      "users": [
        {
          "email": "johnsmith@fakeemail.com",
          "id": 1,
          "name": "John Smith"
        },
        {
          "email": "janedoe2@fakeemail.com",
          "id": 2,
          "name": "Jane Doe"
        },
        ...
      ]
    }
    ```
* **Error Response**
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```

## Create User

Create a new user.

* **URL**: `/users`  
* **Method**: `POST`
* **Authentication**
  * `username`: SuperUser ID  
  * `password`: SuperUser Password
* **Data Params**  
  * **Required**
    * `name=[String]`
    * `email=[Email Address]`
    * `password=[Password]`

* **Success Response**
  * Code: `201`
  * Content:
    ```
    {
      "user": {
        "email": "janedoe@fakeemail.com",
        "id": 2,
        "name": "Jane Doe"
      }
    }
    ```
* **Error Response**
  * Code: `400`
  * Content:
    ```
    {
      "code": "401",
      "error": "Bad Request",
      "message": "Please check request data"
    }
    ```
  OR
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```
  OR
  * Code: `409`
  * Content:
    ```
    {
      "code": "401",
      "error": "Conflict",
      "message": "A user with this email already exists"
    }
    ```

## Get User

Retrieve a single user.

* **URL**: `/user/:id`  
* **Method**: `GET`
* **Authentication**
  * `username`: SuperUser ID  
  * `password`: SuperUser Password
* **Success Response**
  * Code: `200`
  * Content:
    ```
    {
      "user": {
        "email": "janedoe@fakeemail.com",
        "id": 2,
        "name": "Jane Doe"
      }
    }
    ```
* **Error Response**
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```
  OR
  * Code: `404`
  * Content:
    ```
    {
      "error": "Not Found",
      "code": "404",
      "message": "There is not a user with the id=1000"
    }
    ```

## Get All API Keys

Retrieve all API Keys associated with a user.

* **URL**: `/api_keys`  
* **Method**; `GET`
* **Authentication**
  * `username`: User ID  
  * `password`: User Password
* **Success Response**
  * Code: `200`
  * Content:
    ```
    {
      "api_keys": [
        {
          "id": "123456",
          "secret": "Djie83WjfhuC73dDw84",
          "user_id": 1
        },
        {
          "id": "abcdef",
          "secret": "2ijdDiEju93jbnZD93n",
          "user_id": 1
        },
        ...
      ]
    }
    ```
* **Error Response**
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
	```

## Create API Key

Create a new API Key.

* **URL**: `/api_keys`  
* **Method**: `POST`
* **Authentication**
  * `username`: User ID  
  * `password`: User Password
* **Data Params**  
  None
* **Success Response**
  * Code: `201`
  * Content:
    ```
    {
      "api_key": {
        "id": "123456",
        "secret": "Djie83WjfhuC73dDw84",
        "user_id": 1
      }
    }
    ```
* **Error Response**
  * Code: `401`
  * Content:
    ```
    {
      "code": "401",
      "error": "Unauthorized",
      "message": "You must be authenticated to access"
    }
    ```
