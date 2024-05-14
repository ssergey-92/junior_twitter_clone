"""Module for testing class HandleEndpoint from app.models.py ."""
from os import environ as os_environ, listdir as os_listdir

from fastapi import UploadFile
from pytest import mark as pytest_mark, raises as pytest_raises

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

supported_media_files_data = {
    "file_names": (FILE_NAME_1, FILE_NAME_2, FILE_NAME_3),
    "result": True,
}
unsupported_media_files_data = {
    "file_names": ("extension.svg", "extension.pjpeg", "extension.jfif"),
    "result": False,
}
media_files_data = (supported_media_files_data, unsupported_media_files_data)
unsafe_media_file_name = (
    "un.safe.jpg",
    "un'safe.jpg",
    "un}safe.jpg",
)
new_file_name = "new_file_name.jpg"
new_tweets_to_add = (
    {
        "new_tweet": {"tweet_data": "tweet # 4"},
        "api_key": test_user_1["name"],
        "result": {
            "message": {"tweet_id": 4}, "status_code": CREATED_STATUS_CODE,
        },
    },
    {
        "new_tweet": {"tweet_data": "tweet # 5"},
        "api_key": test_user_1["name"],
        "result": {
            "message": {"tweet_id": 5}, "status_code": CREATED_STATUS_CODE,
        },
    },
)
valid_add_media_files_data = (
    {
        "file": UploadFile(
            filename="new_file.jpg", file=open_test_image(FILE_NAME_1),
        ),
        "api_key": test_user_1["name"],
        "result": {
            "message": {"media_id": 4}, "status_code": CREATED_STATUS_CODE,
        },
    },
)
unregister_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
bad_request_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
forbidden_response = {
            "message": ERROR_MESSAGE, "status_code": FORBIDDEN_STATUS_CODE,
        }
invalid_add_media_files_data = (
    {
        "file": UploadFile(
            filename="new_file.ggg", file=open_test_image(FILE_NAME_1),
        ),
        "api_key": test_user_1["name"],
        "result": bad_request_response,
    },
    {
        "file": UploadFile(file=open_test_image(FILE_NAME_1)),
        "api_key": test_user_1["name"],
        "result":  bad_request_response,
    },
)
valid_delete_tweet_data = {
    "api_key": test_user_1["name"],
    "tweet_id": TWEET_1["id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
invalid_delete_tweet_data = {
    "api_key": test_user_1["name"],  # belongs to test_user_1
    "tweet_id": TWEET_2["id"],
    "result": forbidden_response,
}
valid_data_dislike_tweet = {
    "api_key": LIKE_1_1["user_name"],
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
invalid_data_dislike_tweet = {
    "api_key": test_user_2["name"],  # Only test_user_1 liked tweet
    "tweet_id": TWEET_1["id"],
    "result": bad_request_response,
}
valid_data_like_tweet = {
    "api_key": test_user_2["name"],
    "tweet_id": TWEET_1["id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
invalid_data_like_tweet = {
    "api_key": LIKE_1_1["user_name"],  # user has already liked tweet
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": bad_request_response,
}
user_can_follow_user = {
    "api_key": test_user_1["name"],
    "followed_id": 3,
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
unexist_user = {
    "id": 0,
    "name": "unexsit_user",
}
user_cannot_follow_user = (
    {
        "api_key": test_user_1["name"],  # user has already followed him
        "followed_id": test_user_1["followed"][0]["id"],
        "result": bad_request_response,
    },
    {
        "api_key": unexist_user["name"],
        "followed_id": test_user_1["followed"][0]["id"],
        "result": unregister_response,
    },
    {
        "api_key": test_user_1["name"],
        "followed_id": 0,  # followed user is not existed
        "result": unregister_response,
    },
)
user_can_unfollow_user = {
    "api_key": test_user_1["name"],
    "followed_id": test_user_1["followed"][0]["id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
user_cannot_unfollow_user = (
    {
        "api_key": test_user_1["name"],  # user does not follow him
        "followed_id": 3,
        "result": bad_request_response,
    },
    {
        "api_key": unexist_user["name"],
        "followed_id": test_user_1["followed"][0]["id"],
        "result": unregister_response,
    },
    {
        "api_key": test_user_1["name"],
        "followed_id": 0,  # followed user is not existed
        "result": unregister_response,
    },
)
invalid_data_get_user_profile = {
    "result": unregister_response, "id": unexist_user["id"],
}
invalid_data_get_own_profile = {
    "result": unregister_response, "api_key": unexist_user["name"],
}


class TestHandleEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_create_user_profile(init_test_data_for_db: None) -> None:
        user = await User.get_user_by_id(test_user_profile["id"])
        assert HandleEndpoint._create_user_profile(user) == test_user_profile

    @staticmethod
    def test_check_media_file_extension() -> None:
        for i_media_file_data in media_files_data:
            for i_file_name in i_media_file_data["file_names"]:
                is_supported = (
                    HandleEndpoint._is_supported_media_file_extension(
                        i_file_name,
                    )
                )
                assert is_supported == i_media_file_data["result"]

    @staticmethod
    def test_make_safe_file_name() -> None:
        for i_file_name in unsafe_media_file_name:
            safe_file_name = HandleEndpoint._make_safe_file_name(i_file_name)
            safe_file_name = safe_file_name.split(".")
            assert int(safe_file_name[0])
            assert safe_file_name[1] == i_file_name.split(".")[-1]
        for i_file_name in supported_media_files_data["file_names"]:
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
        add_paths_to_os_environ: None,
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
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await HandleEndpoint._delete_media_files(
            TWEET_2["author_name"], TWEET_2["tweet_media_ids"],
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_save_media_file_in_sys(
        add_paths_to_os_environ: None, init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        upload_file = UploadFile(
            filename=FILE_NAME_1, file=open_test_image(FILE_NAME_1),
        )
        await HandleEndpoint._save_media_file_in_sys(
            upload_file, new_file_name,
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images + 1 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_tweet(
        add_paths_to_os_environ: None, init_test_data_for_db: None,
    ) -> None:
        for i_data in new_tweets_to_add:
            message, status_code = await HandleEndpoint.add_tweet(
                i_data["api_key"], i_data["new_tweet"],
            )
            assert message == i_data["result"]["message"]
            assert status_code == i_data["result"]["status_code"]

    @staticmethod
    def test_get_get_save_media_files_path(
            add_paths_to_os_environ: None,
            reset_os_environ_paths: None,
    ) -> None:
        assert isinstance(HandleEndpoint._get_save_media_files_path(), str)
        os_environ.pop("SAVE_MEDIA_PATH")
        with pytest_raises(SystemExit):
            HandleEndpoint._get_save_media_files_path()

    @staticmethod
    def test_create_unregister_response() -> None:
        message, status_code = HandleEndpoint._create_unregister_response()
        assert status_code == unregister_response["status_code"]
        assert message.keys() == unregister_response["message"].keys()
        assert message["result"] == unregister_response["message"]["result"]
        assert isinstance(message["error_type"], str)
        assert isinstance(message["error_message"], str)

    @staticmethod
    def test_create_bad_request_response() -> None:
        error_details = "bad request details"
        message, status_code = HandleEndpoint._create_bad_request_response(
            error_details,
        )
        assert status_code == bad_request_response["status_code"]
        assert message.keys() == bad_request_response["message"].keys()
        assert message["result"] == bad_request_response["message"]["result"]
        assert message["error_message"] == error_details
        assert isinstance(message["error_type"], str)

    @staticmethod
    def test_create_forbidden_response() -> None:
        error_details = "forbidden details"
        message, status_code = HandleEndpoint._create_forbidden_response(
            error_details,
        )
        assert status_code == forbidden_response["status_code"]
        assert message.keys() == forbidden_response["message"].keys()
        assert message["result"] == forbidden_response["message"]["result"]
        assert message["error_message"] == error_details
        assert isinstance(message["error_type"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_media_file(
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        for i_data in valid_add_media_files_data:
            message, status_code = await HandleEndpoint.add_media_file(
                i_data["api_key"], i_data["file"],
            )
            assert message == i_data["result"]["message"]
            assert status_code == i_data["result"]["status_code"]
        for i_data in invalid_add_media_files_data:
            message, status_code = await HandleEndpoint.add_media_file(
                i_data["api_key"], i_data["file"],
            )
            assert message.keys() == i_data["result"]["message"].keys()
            assert message["result"] == i_data["result"]["message"]["result"]
            assert status_code == i_data["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_tweet(
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        message, status_code = await HandleEndpoint.delete_tweet(
            valid_delete_tweet_data["api_key"],
            valid_delete_tweet_data["tweet_id"],
        )
        assert message == valid_delete_tweet_data["result"]["message"]
        assert status_code == valid_delete_tweet_data["result"]["status_code"]
        message, status_code = await HandleEndpoint.delete_tweet(
            invalid_delete_tweet_data["api_key"],
            invalid_delete_tweet_data["tweet_id"],
        )
        assert (message.keys() ==
                invalid_delete_tweet_data["result"]["message"].keys())
        assert (message["result"] ==
                invalid_delete_tweet_data["result"]["message"]["result"])
        assert (status_code ==
                invalid_delete_tweet_data["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_dislike_tweet_by_id(init_test_data_for_db: None) -> None:
        message, status_code = await HandleEndpoint.dislike_tweet_by_id(
            valid_data_dislike_tweet["api_key"],
            valid_data_dislike_tweet["tweet_id"],
        )
        assert message == valid_data_dislike_tweet["result"]["message"]
        assert status_code == valid_data_dislike_tweet["result"]["status_code"]
        message, status_code = await HandleEndpoint.dislike_tweet_by_id(
            invalid_data_dislike_tweet["api_key"],
            invalid_data_dislike_tweet["tweet_id"],
        )
        assert (message.keys() ==
                invalid_data_dislike_tweet["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_dislike_tweet["result"]["message"]["result"])
        assert (status_code ==
                invalid_data_dislike_tweet["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_like_tweet_by_id(init_test_data_for_db: None) -> None:
        message, status_code = await HandleEndpoint.like_tweet_by_id(
            valid_data_like_tweet["api_key"],
            valid_data_like_tweet["tweet_id"],
        )
        assert message == valid_data_like_tweet["result"]["message"]
        assert status_code == valid_data_like_tweet["result"]["status_code"]
        message, status_code = await HandleEndpoint.like_tweet_by_id(
            invalid_data_like_tweet["api_key"],
            invalid_data_like_tweet["tweet_id"],
        )
        assert (message.keys() ==
                invalid_data_like_tweet["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_like_tweet["result"]["message"]["result"])
        assert status_code == invalid_data_like_tweet["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_full_tweet_feed(init_test_data_for_db: None) -> None:
        tweet_feed, status_code = await HandleEndpoint.get_full_tweet_feed()
        assert tweet_feed == CORRECT_GET_TWEET_FEED_RESPONSE["tweet_feed"]
        assert status_code == CORRECT_GET_TWEET_FEED_RESPONSE["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_full_tweet_feed_from_empty_tables(
            recreate_all_tables: None,
    ) -> None:
        tweet_feed, status_code = await HandleEndpoint.get_full_tweet_feed()
        assert tweet_feed == CORRECT_GET_TWEET_FEED_RESPONSE_2["tweet_feed"]
        assert status_code == CORRECT_GET_TWEET_FEED_RESPONSE_2["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_profile(init_test_data_for_db: None) -> None:
        user_profile, status_code = await HandleEndpoint.get_user_profile(
            CORRECT_GET_USER_PROFILE_RESPONSE["profile"]["user"]["id"],
        )
        assert (user_profile ==
                CORRECT_GET_USER_PROFILE_RESPONSE["profile"])
        assert (status_code ==
                CORRECT_GET_USER_PROFILE_RESPONSE["status_code"])
        message, status_code = await HandleEndpoint.get_user_profile(
            invalid_data_get_user_profile["id"],
        )
        assert (message.keys() ==
                invalid_data_get_user_profile["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_get_user_profile["result"]["message"]["result"])
        assert (status_code ==
                invalid_data_get_user_profile["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_own_profile(init_test_data_for_db: None) -> None:
        own_profile, status_code = await HandleEndpoint.get_own_profile(
            CORRECT_GET_OWN_PROFILE_RESPONSE["profile"]["user"]["name"],
        )
        assert own_profile == CORRECT_GET_OWN_PROFILE_RESPONSE["profile"]
        assert status_code == CORRECT_GET_OWN_PROFILE_RESPONSE["status_code"]
        message, status_code = await HandleEndpoint.get_own_profile(
            invalid_data_get_own_profile["api_key"],
        )
        assert (message.keys() ==
                invalid_data_get_own_profile["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_get_own_profile["result"]["message"]["result"])
        assert (status_code ==
                invalid_data_get_own_profile["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_follow_other_user(init_test_data_for_db: None) -> None:
        message, status_code = await HandleEndpoint.follow_other_user(
            user_can_follow_user["api_key"],
            user_can_follow_user["followed_id"],
        )
        assert message == user_can_follow_user["result"]["message"]
        assert status_code == user_can_follow_user["result"]["status_code"]
        for i_data in user_cannot_follow_user:
            message, status_code = await HandleEndpoint.follow_other_user(
                i_data["api_key"], i_data["followed_id"],
            )
            assert message.keys() == i_data["result"]["message"].keys()
            assert message["result"] == i_data["result"]["message"]["result"]
            assert status_code == i_data["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_unfollow_other_user(init_test_data_for_db: None) -> None:
        message, status_code = await HandleEndpoint.unfollow_user(
            user_can_unfollow_user["api_key"],
            user_can_unfollow_user["followed_id"],
        )
        assert message == user_can_unfollow_user["result"]["message"]
        assert status_code == user_can_unfollow_user["result"]["status_code"]
        for i_data in user_cannot_unfollow_user:
            message, status_code = await HandleEndpoint.unfollow_user(
                i_data["api_key"], i_data["followed_id"],
            )
            assert message.keys() == i_data["result"]["message"].keys()
            assert message["result"] == i_data["result"]["message"]["result"]
            assert status_code == i_data["result"]["status_code"]
