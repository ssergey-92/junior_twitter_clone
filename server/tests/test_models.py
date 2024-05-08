from os import listdir as os_listdir

from fastapi import UploadFile
from pytest import mark as pytest_mark

from ..app.database import Tweet, User
from ..app.models import HandleEndpoint
from .common_data_for_tests import (
    BAD_REQUEST_STATUS_CODE,
    CORRECT_GET_OWN_PROFILE_RESPONSE,
    CORRECT_GET_TWEET_FEED_RESPONSE,
    CORRECT_GET_TWEET_FEED_RESPONSE_2,
    CORRECT_GET_USER_PROFILE_RESPONSE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    FILE_NAME_1,
    FILE_NAME_2,
    FILE_NAME_3,
    FORBIDDEN_STATUS_CODE,
    LIKE_1_1,
    OK_STATUS_CODE,
    SAVE_MEDIA_ABS_PATH,
    SORTED_TWEET_FEED,
    TWEET_1,
    TWEET_2,
    open_test_image,
    test_user_1,
    test_user_2,
    test_user_profile,
)

ALLOWED_MEDIA_FILES = (FILE_NAME_1, FILE_NAME_2, FILE_NAME_3)
WRONG_MEDIA_FILE_EXTENSIONS = (
    "extension.svg",
    "extension.pjpeg",
    "extension.jfif",
)
UNSAFE_MEDIA_FILE_NAME = (
    "un.safe.jpg",
    "un'safe.jpg",
    "un}safe.jpg",
)
NEW_FILE_NAME = "new_file_name.jpg"
NEW_TWEETS_TO_ADD = [
    {
        "new_tweet": {"tweet_data": "tweet # 4"},
        "api_key": test_user_1["name"],
        "result": ({"tweet_id": 4}, CREATED_STATUS_CODE),
    },
    {
        "new_tweet": {"tweet_data": "tweet # 5"},
        "api_key": test_user_1["name"],
        "result": ({"tweet_id": 5}, CREATED_STATUS_CODE),
    },
]
CORRECT_NEW_MEDIA_FILES_DATA = {
    "file": UploadFile(
        filename="new_file.jpg", file=open_test_image(FILE_NAME_1)
    ),
    "api_key": test_user_1["name"],
    "result": ({"media_id": 4}, CREATED_STATUS_CODE),
}
INCORRECT_NEW_MEDIA_FILES_DATA = {
    "file": UploadFile(
        filename="new_file.ggg", file=open_test_image(FILE_NAME_1)
    ),
    "api_key": test_user_1["name"],
    "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
}
CORRECT_TWEET_TO_DELETE_DATA = {
    "api_key": test_user_1["name"],
    "tweet_id": TWEET_1["id"],
    "result": (None, OK_STATUS_CODE),
}
INCORRECT_TWEET_TO_DELETE_DATA = {
    "api_key": test_user_1["name"],  # belongs to test_user_1
    "tweet_id": TWEET_2["id"],
    "result": (ERROR_MESSAGE, FORBIDDEN_STATUS_CODE),
}
CORRECT_DATA_TO_DISLIKE_TWEET = {
    "api_key": LIKE_1_1["user_name"],
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": (None, CREATED_STATUS_CODE),
}
INCORRECT_DATA_TO_DISLIKE_TWEET = {
    "api_key": test_user_2["name"],  # Only test_user_1 liked tweet
    "tweet_id": TWEET_1["id"],
    "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
}
CORRECT_DATA_TO_LIKE_TWEET = {
    "api_key": test_user_2["name"],
    "tweet_id": TWEET_1["id"],
    "result": (None, CREATED_STATUS_CODE),
}
INCORRECT_DATA_TO_LIKE_TWEET = {
    "api_key": LIKE_1_1["user_name"],  # user has already liked tweet
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
}
USER_CAN_FOLLOW_USER = {
    "api_key": test_user_1["name"],
    "followed_id": 3,
    "result": {"message": None, "http_status_code": CREATED_STATUS_CODE},
}
USER_CANNOT_FOLLOW_USER = {  # user has already followed him
    "api_key": test_user_1["name"],
    "followed_id": test_user_1["followed"][0]["id"],
    "result": {
        "message": ERROR_MESSAGE,
        "http_status_code": BAD_REQUEST_STATUS_CODE,
    },
}
USER_CAN_UNFOLLOW_USER = {
    "api_key": test_user_1["name"],
    "followed_id": test_user_1["followed"][0]["id"],
    "result": {"message": None, "http_status_code": CREATED_STATUS_CODE},
}
USER_CANNOT_UNFOLLOW_USER = {  # user does not follow him
    "api_key": test_user_1["name"],
    "followed_id": 3,
    "result": {
        "message": ERROR_MESSAGE,
        "http_status_code": BAD_REQUEST_STATUS_CODE,
    },
}


class TestHandleEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_create_user_profile(init_test_data_for_db: None) -> None:
        user = await User.get_user_by_id(test_user_profile["id"])
        assert HandleEndpoint._create_user_profile(user) == test_user_profile

    @staticmethod
    def test_check_media_file_extension() -> None:
        for i_media_file in ALLOWED_MEDIA_FILES:
            result = HandleEndpoint._is_supported_media_file_extension(
                i_media_file,
            )
            assert result is True
        for i_media_file in WRONG_MEDIA_FILE_EXTENSIONS:
            result = HandleEndpoint._is_supported_media_file_extension(
                i_media_file,
            )
            assert result is False


    @staticmethod
    def test_make_safe_file_name() -> None:
        for i_file_name in UNSAFE_MEDIA_FILE_NAME:
            safe_file_name = HandleEndpoint._make_safe_file_name(i_file_name)
            safe_file_name = safe_file_name.split(".")
            assert int(safe_file_name[0])
            assert safe_file_name[1] == i_file_name.split(".")[-1]
        for i_file_name in ALLOWED_MEDIA_FILES:
            safe_file_name = HandleEndpoint._make_safe_file_name(i_file_name)
            assert safe_file_name == i_file_name

    @staticmethod
    @pytest_mark.asyncio
    async def test_create_tweet_feed(init_test_data_for_db: None) -> None:
        all_sorted_tweets = await Tweet.get_all_tweets_sorted_by_likes()
        tweet_feed = await HandleEndpoint._create_tweet_feed(all_sorted_tweets)
        assert tweet_feed == SORTED_TWEET_FEED

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_files_from_sys(
        add_media_path_to_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await HandleEndpoint._delete_files_from_sys([FILE_NAME_1, FILE_NAME_2])
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_media_files(
        add_media_path_to_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await HandleEndpoint._delete_media_files(
            TWEET_2["author_name"], TWEET_2["tweet_media_ids"]
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_save_media_file_in_sys(
        add_media_path_to_environ: None, init_midia_file_for_test: None
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        upload_file = UploadFile(
            filename=FILE_NAME_1, file=open_test_image(FILE_NAME_1)
        )
        await HandleEndpoint._save_media_file_in_sys(
            upload_file, NEW_FILE_NAME
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images + 1 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_tweet(
        add_media_path_to_environ: None, init_test_data_for_db: None
    ) -> None:
        for i_tweet_details in NEW_TWEETS_TO_ADD:
            result = await HandleEndpoint.add_tweet(
                api_key=i_tweet_details["api_key"],
                new_tweet=i_tweet_details["new_tweet"],
            )
            assert result == i_tweet_details["result"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_media_file(
        add_media_path_to_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        result = await HandleEndpoint.add_media_file(
            api_key=CORRECT_NEW_MEDIA_FILES_DATA["api_key"],
            media_file=CORRECT_NEW_MEDIA_FILES_DATA["file"],
        )
        assert result == CORRECT_NEW_MEDIA_FILES_DATA["result"]
        result = await HandleEndpoint.add_media_file(
            api_key=INCORRECT_NEW_MEDIA_FILES_DATA["api_key"],
            media_file=INCORRECT_NEW_MEDIA_FILES_DATA["file"],
        )
        assert (
            result[0].keys()
            == INCORRECT_NEW_MEDIA_FILES_DATA["result"][0].keys()
        )
        assert result[1] == INCORRECT_NEW_MEDIA_FILES_DATA["result"][1]
        assert len(result) == len(INCORRECT_NEW_MEDIA_FILES_DATA["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_tweet(
        add_media_path_to_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        result = await HandleEndpoint.delete_tweet(
            api_key=CORRECT_TWEET_TO_DELETE_DATA["api_key"],
            tweet_id=CORRECT_TWEET_TO_DELETE_DATA["tweet_id"],
        )
        assert result == CORRECT_TWEET_TO_DELETE_DATA["result"]
        result = await HandleEndpoint.delete_tweet(
            api_key=INCORRECT_TWEET_TO_DELETE_DATA["api_key"],
            tweet_id=INCORRECT_TWEET_TO_DELETE_DATA["tweet_id"],
        )
        assert (
            result[0].keys()
            == INCORRECT_TWEET_TO_DELETE_DATA["result"][0].keys()
        )
        assert result[1] == INCORRECT_TWEET_TO_DELETE_DATA["result"][1]
        assert len(result) == len(INCORRECT_TWEET_TO_DELETE_DATA["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_dislike_tweet_by_id(init_test_data_for_db: None) -> None:
        result = await HandleEndpoint.dislike_tweet_by_id(
            api_key=CORRECT_DATA_TO_DISLIKE_TWEET["api_key"],
            tweet_id=CORRECT_DATA_TO_DISLIKE_TWEET["tweet_id"],
        )
        assert result == CORRECT_DATA_TO_DISLIKE_TWEET["result"]
        result = await HandleEndpoint.dislike_tweet_by_id(
            api_key=INCORRECT_DATA_TO_DISLIKE_TWEET["api_key"],
            tweet_id=INCORRECT_DATA_TO_DISLIKE_TWEET["tweet_id"],
        )
        assert (
            result[0].keys()
            == INCORRECT_DATA_TO_DISLIKE_TWEET["result"][0].keys()
        )
        assert result[1] == INCORRECT_DATA_TO_DISLIKE_TWEET["result"][1]
        assert len(result) == len(INCORRECT_DATA_TO_DISLIKE_TWEET["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_like_tweet_by_id(init_test_data_for_db: None) -> None:
        result = await HandleEndpoint.like_tweet_by_id(
            api_key=CORRECT_DATA_TO_LIKE_TWEET["api_key"],
            tweet_id=CORRECT_DATA_TO_LIKE_TWEET["tweet_id"],
        )
        assert result == CORRECT_DATA_TO_LIKE_TWEET["result"]
        result = await HandleEndpoint.like_tweet_by_id(
            api_key=INCORRECT_DATA_TO_LIKE_TWEET["api_key"],
            tweet_id=INCORRECT_DATA_TO_LIKE_TWEET["tweet_id"],
        )
        assert (
            result[0].keys()
            == INCORRECT_DATA_TO_LIKE_TWEET["result"][0].keys()
        )
        assert result[1] == INCORRECT_DATA_TO_LIKE_TWEET["result"][1]
        assert len(result) == len(INCORRECT_DATA_TO_LIKE_TWEET["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_full_tweet_feed(init_test_data_for_db: None) -> None:
        tweet_feed, http_status_code = (
            await HandleEndpoint.get_full_tweet_feed()
        )
        assert tweet_feed == CORRECT_GET_TWEET_FEED_RESPONSE["tweet_feed"]
        assert (
            http_status_code
            == CORRECT_GET_TWEET_FEED_RESPONSE["http_status_code"]
        )

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_full_tweet_feed_from_empty_tables(
        recreate_all_tables: None,
    ) -> None:
        tweet_feed, http_status_code = (
            await HandleEndpoint.get_full_tweet_feed()
        )
        assert tweet_feed == CORRECT_GET_TWEET_FEED_RESPONSE_2["tweet_feed"]
        assert (
            http_status_code
            == CORRECT_GET_TWEET_FEED_RESPONSE_2["http_status_code"]
        )

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_profile_details(
        init_test_data_for_db: None,
    ) -> None:
        user_id = (CORRECT_GET_USER_PROFILE_RESPONSE)["user_profile"]["user"][
            "id"
        ]
        user_profile, http_status_code = (
            await HandleEndpoint.get_user_profile_details(user_id)
        )
        assert (
            user_profile == CORRECT_GET_USER_PROFILE_RESPONSE["user_profile"]
        )
        assert (
            http_status_code
            == CORRECT_GET_USER_PROFILE_RESPONSE["http_status_code"]
        )

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_own_profile_details(
        init_test_data_for_db: None,
    ) -> None:
        apy_key = CORRECT_GET_OWN_PROFILE_RESPONSE["own_profile"]["user"][
            "name"
        ]
        own_profile, http_status_code = (
            await HandleEndpoint.get_own_profile_details(apy_key)
        )
        assert own_profile == CORRECT_GET_OWN_PROFILE_RESPONSE["own_profile"]
        assert (
            http_status_code
            == CORRECT_GET_OWN_PROFILE_RESPONSE["http_status_code"]
        )

    @staticmethod
    @pytest_mark.asyncio
    async def test_follow_other_user(init_test_data_for_db: None) -> None:
        message, http_status_code = await HandleEndpoint.follow_other_user(
            api_key=USER_CAN_FOLLOW_USER["api_key"],
            followed_id=USER_CAN_FOLLOW_USER["followed_id"],
        )
        expected_result = USER_CAN_FOLLOW_USER["result"]
        assert message == expected_result["message"]
        assert http_status_code == expected_result["http_status_code"]
        message, http_status_code = await HandleEndpoint.follow_other_user(
            api_key=USER_CANNOT_FOLLOW_USER["api_key"],
            followed_id=USER_CANNOT_FOLLOW_USER["followed_id"],
        )
        expected_result = USER_CANNOT_FOLLOW_USER["result"]
        assert http_status_code == expected_result["http_status_code"]
        assert (
            message.get("result", None) == expected_result["message"]["result"]
        )
        assert message.keys() == expected_result["message"].keys()
        assert isinstance(message.get("error_type", None), str)
        assert isinstance(message.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_unfollow_other_user(init_test_data_for_db: None) -> None:
        message, http_status_code = await HandleEndpoint.unfollow_user(
            api_key=USER_CAN_UNFOLLOW_USER["api_key"],
            followed_id=USER_CAN_UNFOLLOW_USER["followed_id"],
        )
        expected_result = USER_CAN_UNFOLLOW_USER["result"]
        assert message == expected_result["message"]
        assert http_status_code == expected_result["http_status_code"]
        message, http_status_code = await HandleEndpoint.unfollow_user(
            api_key=USER_CANNOT_UNFOLLOW_USER["api_key"],
            followed_id=USER_CANNOT_UNFOLLOW_USER["followed_id"],
        )
        expected_result = USER_CANNOT_UNFOLLOW_USER["result"]
        assert http_status_code == expected_result["http_status_code"]
        assert (
            message.get("result", None) == expected_result["message"]["result"]
        )
        assert message.keys() == expected_result["message"].keys()
        assert isinstance(message.get("error_type", None), str)
        assert isinstance(message.get("error_message", None), str)
