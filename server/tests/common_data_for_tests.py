from os import path as os_path, environ as os_environ
from typing import BinaryIO

OK_STATUS_CODE = 200
CREATED_STATUS_CODE = 201
BAD_REQUEST_STATUS_CODE = 400
UNAUTHORIZED_SATUS_CODE = 401
FORBIDDEN_STATUS_CODE = 403
NOT_FOUND_SATUS_CODE = 404
METHOD_NOT_ALLOWED_SATUS_CODE = 405
FAKE_TWITTER_ENDPOINTS = {
    "add_tweet": {"endpoint": "/api/tweets", "http_method": "POST"},
    "add_media": {"endpoint": "/api/medias", "http_method": "POST"},
    "delete_tweet": {"endpoint": "/api/tweets/{id}", "http_method": "DELETE"},
    "like_tweet": {
        "endpoint": "/api/tweets/{id}/likes",
        "http_method": "POST"
    },
    "dislike_tweet": {
        "endpoint": "/api/tweets/{id}/likes", "http_method": "DELETE"
    },
    "follow_user": {
        "endpoint": "/api/users/{id}/follow", "http_method": "POST"}
    ,
    "unfollow_user": {
        "endpoint": "/api/users/{id}/follow", "http_method": "DELETE"
    },
    "get_tweet_feed": {"endpoint": "/api/tweets", "http_method": "GET"},
    "get_own_profile": {"endpoint": "/api/users/me", "http_method": "GET"},
    "get_user_profile": {
        "endpoint": "/api/users/{id}", "http_method": "GET"
    }
}
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
test_user_1 = {"name": "test_1", "id": 1}
test_user_2 = {"name": "test_2", "id": 2}
test_user_3 = {"name": "test_3", "id": 3}
test_user_1["followers"] = [
    {"name": test_user_3["name"], "id": test_user_3["id"]}
]
test_user_2["followers"] = [
    {"name": test_user_1["name"], "id": test_user_1["id"]}
]
test_user_3["followers"] = []
test_user_1["followed"] = [
    {"name": test_user_2["name"], "id": test_user_2["id"]}
]
test_user_2["followed"] = []
test_user_3["followed"] = [
    {"name": test_user_1["name"], "id": test_user_1["id"]}
]
AUTHORIZED_HEADER = {"api-key": test_user_1["name"]}

FILE_NAME_1 = "image.png"
FILE_NAME_2 = "image.jpg"
FILE_NAME_3 = "image.jpeg"
MEDIA_FILE_NAME_FOR_RENAME = "image!@#.jpg"
MEDIA_FILE_UNSUPPORTED_FORMAT = "image.txt"
MEDIA_FILE_1 = {
    "file_name": FILE_NAME_1, "user_name": test_user_1["name"], "id": 1
}
MEDIA_FILE_2 = {
    "file_name": FILE_NAME_2, "user_name": test_user_2["name"], "id": 2
}
MEDIA_FILE_3 = {
    "file_name": FILE_NAME_3, "user_name": test_user_2["name"], "id": 3
}
DEFAULT_TOTAL_MEDIA_FILES = 3
TWEET_1 = {
    "author_name": test_user_1["name"],
    "tweet_data": "tweet of test_1 user",
    "tweet_media_ids": [1],
    "id": 1
}
TWEET_2 = {
    "author_name": test_user_2["name"],
    "tweet_data": "tweet of test_2 user",
    "tweet_media_ids": [2, 3],
    "id": 2
}
TWEET_3 = {
    "author_name": test_user_3["name"],
    "tweet_data": "tweet of test_3 user",
    "id": 3
}
DEFAULT_TOTAL_TWEETS = 3
LIKE_1_1 = {"tweet_id": 1, "user_name": test_user_1["name"], "id": 1}
LIKE_2_2 = {"tweet_id": 2, "user_name": test_user_2["name"], "id": 2}
LIKE_2_3 = {"tweet_id": 2, "user_name": test_user_3["name"], "id": 3}
LIKE_3_1 = {"tweet_id": 3, "user_name": test_user_1["name"], "id": 4}
LIKE_3_2 = {"tweet_id": 3, "user_name": test_user_2["name"], "id": 5}
LIKE_3_3 = {"tweet_id": 3, "user_name": test_user_3["name"], "id": 6}
DEFAULT_TOTAL_LIKES = 6
SORTED_TWEET_FEED = [
    {
        "id": TWEET_3["id"],
        "content": TWEET_3["tweet_data"],
        "attachments": [],
        "author": {"id": test_user_3["id"], "name": TWEET_3["author_name"]},
        "likes": [
            {"user_id": test_user_1["id"], "name": test_user_1["name"]},
            {"user_id": test_user_2["id"], "name": test_user_2["name"]},
            {"user_id": test_user_3["id"], "name": test_user_3["name"]}
        ]
    },
    {
        "id": TWEET_2["id"],
        "content": TWEET_2["tweet_data"],
        "attachments": [FILE_NAME_2, FILE_NAME_3],
        "author": {"id": test_user_2["id"], "name": TWEET_2["author_name"]},
        "likes": [
            {"user_id": test_user_2["id"], "name": test_user_2["name"]},
            {"user_id": test_user_3["id"], "name": test_user_3["name"]}
        ]
    },
    {
        "id": TWEET_1["id"],
        "content": TWEET_1["tweet_data"],
        "attachments": [FILE_NAME_1],
        "author": {'id': test_user_1["id"], 'name': TWEET_1["author_name"]},
        "likes": [{"user_id": test_user_1["id"], "name": test_user_1["name"]}]
    }
]


def open_test_image(file_name: str) -> BinaryIO:
    abs_image_path = os_path.abspath(
        os_path.join(DEFAULT_TEST_IMAGES_PATH, file_name)
    )
    return open(abs_image_path, 'rb')
