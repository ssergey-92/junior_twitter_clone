from os import path as os_path, environ as os_environ
from typing import BinaryIO

from aiofiles import open as aio_open, os as aio_os

OK_STATUS_CODE = 200

CREATED_STATUS_CODE = 201

BAD_REQUEST_STATUS_CODE = 400

UNAUTHORIZED_SATUS_CODE = 401

FORBIDDEN_STATUS_CODE = 403

NOT_FOUND_SATUS_CODE = 404
METHOD_NOT_ALLOWED_SATUS_CODE = 405
ADD_TWEET_ENDPOINT = "/api/tweets"
ADD_MEDIA_ENDPOINT = "/api/medias"
delete_tweet_endpoint = '/api/tweets/{id}'
like_tweet_endpoint = '/api/tweets/{id}/likes'
dislike_tweet_endpoint = '/api/tweets/{id}/likes'
FAKE_TWITTER_ENDPOINTS = [
    ('/api/tweets', 'POST'),
    ('/api/medias', 'POST'),
    ('/api/tweets/{id}', 'DELETE'),
    ('/api/tweets/{id}/likes', 'POST'),
    ('/api/tweets/{id}/likes', 'DELETE'),
    ('/api/users/{id}/follow', 'POST'),
    ('/api/users/{id}/follow', 'DELETE'),
    ('/api/tweets', 'GET'),
    ('/api/users/me', 'GET'),
    ('/api/users/{id}', 'GET')
]
ERROR_MESSAGE = {
    "result": False,
    "error_type": "",
    "error_message": ""
}
FILE_DIR_PATH = os_path.dirname(__file__)
DEFAULT_TEST_IMAGES_PATH = os_path.join(FILE_DIR_PATH, "test_images/default")
SAVE_MEDIA_ABS_PATH = os_path.join(
    FILE_DIR_PATH, os_environ.get("SAVE_MEDIA_REL_PATH")
)
TEST_USER_1 = {"name": "test_1"}
AUTHORIZED_HEADER = {"api-key": TEST_USER_1["name"]}
TEST_USER_2 = {"name": "test_2"}
TEST_USER_3 = {"name": "test_3"}
FILE_NAME_1 = "image.png"
FILE_NAME_2 = "image.jpg"
FILE_NAME_3 = "image.jpeg"
MEDIA_FILE_NAME_FOR_RENAME = "image!@#.jpg"
MEDIA_FILE_UNSUPPORTED_FORMAT = "image.txt"
MEDIA_FILE_1 = {"file_name": FILE_NAME_1, "user_name": TEST_USER_1["name"]}
MEDIA_FILE_2 = {"file_name": FILE_NAME_2, "user_name": TEST_USER_2["name"]}
MEDIA_FILE_3 = {"file_name": FILE_NAME_3, "user_name":  TEST_USER_2["name"]}
TWEET_1 = {
    "author_name": TEST_USER_1["name"],
    "tweet_data": "tweet of test_1 user",
    "tweet_media_ids": [1]
}
TWEET_2 = {
    "author_name": TEST_USER_2["name"],
    "tweet_data": "tweet of test_2 user",
    "tweet_media_ids": [2, 3]
}
TWEET_3 = {
    "author_name": TEST_USER_3["name"],
    "tweet_data": "tweet of test_3 user",
}
LIKE_1_1 = {"tweet_id": 1, "user_name": TEST_USER_1["name"]}
LIKE_2_2 = {"tweet_id": 2, "user_name": TEST_USER_2["name"]}
LIKE_2_3 = {"tweet_id": 2, "user_name": TEST_USER_3["name"]}
LIKE_3_1 = {"tweet_id": 3, "user_name": TEST_USER_1["name"]}
LIKE_3_2 = {"tweet_id": 3, "user_name": TEST_USER_2["name"]}
LIKE_3_3 = {"tweet_id": 3, "user_name": TEST_USER_3["name"]}


def open_test_image(file_name: str) -> BinaryIO:
    abs_image_path = os_path.abspath(
        os_path.join(DEFAULT_TEST_IMAGES_PATH, file_name)
    )
    return open(abs_image_path, 'rb')

