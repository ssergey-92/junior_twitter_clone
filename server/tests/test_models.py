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

supported_media_files_data = {
    "file_names": (FILE_NAME_1, FILE_NAME_2, FILE_NAME_3,),
    "result": True,
}
unsupported_media_files_data = {
    "file_names": ("extension.svg", "extension.pjpeg", "extension.jfif",),
    "result": False,
}
media_files_data = (supported_media_files_data, unsupported_media_files_data)
unsafe_media_file_name = (
    "un.safe.jpg",
    "un'safe.jpg",
    "un}safe.jpg",
)
new_file_name = "new_file_name.jpg"
new_tweets_to_add = [
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
valid_add_media_files_data = {
    "file": UploadFile(
        filename="new_file.jpg", file=open_test_image(FILE_NAME_1)
    ),
    "api_key": test_user_1["name"],
    "result": ({"media_id": 4}, CREATED_STATUS_CODE),
}
invalid_add_media_files_data = (
    {
        "file": UploadFile(
            filename="new_file.ggg", file=open_test_image(FILE_NAME_1)
        ),
        "api_key": test_user_1["name"],
        "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
    },
    {
        "file": UploadFile(file=open_test_image(FILE_NAME_1)),
        "api_key": test_user_1["name"],
        "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
    },
)
valid_delete_tweet_data = {
    "api_key": test_user_1["name"],
    "tweet_id": TWEET_1["id"],
    "result": (None, OK_STATUS_CODE),
}
invalid_delete_tweet_data = {
    "api_key": test_user_1["name"],  # belongs to test_user_1
    "tweet_id": TWEET_2["id"],
    "result": (ERROR_MESSAGE, FORBIDDEN_STATUS_CODE),
}
valid_data_to_dislike_tweet = {
    "api_key": LIKE_1_1["user_name"],
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": (None, CREATED_STATUS_CODE),
}
invalid_data_to_dislike_tweet = {
    "api_key": test_user_2["name"],  # Only test_user_1 liked tweet
    "tweet_id": TWEET_1["id"],
    "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
}
valid_data_to_like_tweet = {
    "api_key": test_user_2["name"],
    "tweet_id": TWEET_1["id"],
    "result": (None, CREATED_STATUS_CODE),
}
invalid_data_to_like_tweet = {
    "api_key": LIKE_1_1["user_name"],  # user has already liked tweet
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": (ERROR_MESSAGE, BAD_REQUEST_STATUS_CODE),
}
user_can_follow_user = {
    "api_key": test_user_1["name"],
    "followed_id": 3,
    "result": {"message": None, "http_status_code": CREATED_STATUS_CODE},
}
user_cannot_follow_user = {  # user has already followed him
    "api_key": test_user_1["name"],
    "followed_id": test_user_1["followed"][0]["id"],
    "result": {
        "message": ERROR_MESSAGE,
        "http_status_code": BAD_REQUEST_STATUS_CODE,
    },
}
user_can_unfollow_user = {
    "api_key": test_user_1["name"],
    "followed_id": test_user_1["followed"][0]["id"],
    "result": {"message": None, "http_status_code": CREATED_STATUS_CODE},
}
user_cannot_unfollow_user = {  # user does not follow him
    "api_key": test_user_1["name"],
    "followed_id": 3,
    "result": {
        "message": ERROR_MESSAGE,
        "http_status_code": BAD_REQUEST_STATUS_CODE,
    },
}
invalid_data_get_own_profile = {
    "result": {
        "message": ERROR_MESSAGE,
        "http_status_code": BAD_REQUEST_STATUS_CODE,
    },
    "api_key": "unexsist user"
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
                result = HandleEndpoint._is_supported_media_file_extension(
                    i_file_name,
                )
                assert result == i_media_file_data["result"]

    @staticmethod
    def test_make_safe_file_name() -> None:
        for i_file_name in unsafe_media_file_name:
            safe_file_name = HandleEndpoint._make_safe_file_name(i_file_name)
            safe_file_name = safe_file_name.split(".")
            assert int(safe_file_name[0])
            assert safe_file_name[1] == i_file_name.split(".")[-1]
        for i_file_name in supported_media_files_data:
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
            upload_file, new_file_name
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images + 1 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_tweet(
            add_media_path_to_environ: None, init_test_data_for_db: None
    ) -> None:
        for i_tweet_details in new_tweets_to_add:
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
            api_key=valid_add_media_files_data["api_key"],
            media_file=valid_add_media_files_data["file"],
        )
        assert result == valid_add_media_files_data["result"]
        for i_data in invalid_add_media_files_data:
            result = await HandleEndpoint.add_media_file(
                api_key=i_data["api_key"],
                media_file=i_data["file"],
            )
            assert (
                    result[0].keys()
                    == i_data["result"][0].keys()
            )
            assert result[1] == i_data["result"][1]
            assert len(result) == len(i_data["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_tweet(
            add_media_path_to_environ: None,
            init_test_data_for_db: None,
            init_midia_file_for_test: None,
    ) -> None:
        result = await HandleEndpoint.delete_tweet(
            api_key=valid_delete_tweet_data["api_key"],
            tweet_id=valid_delete_tweet_data["tweet_id"],
        )
        assert result == valid_delete_tweet_data["result"]
        result = await HandleEndpoint.delete_tweet(
            api_key=invalid_delete_tweet_data["api_key"],
            tweet_id=invalid_delete_tweet_data["tweet_id"],
        )
        assert (
                result[0].keys()
                == invalid_delete_tweet_data["result"][0].keys()
        )
        assert result[1] == invalid_delete_tweet_data["result"][1]
        assert len(result) == len(invalid_delete_tweet_data["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_dislike_tweet_by_id(init_test_data_for_db: None) -> None:
        result = await HandleEndpoint.dislike_tweet_by_id(
            api_key=valid_data_to_dislike_tweet["api_key"],
            tweet_id=valid_data_to_dislike_tweet["tweet_id"],
        )
        assert result == valid_data_to_dislike_tweet["result"]
        result = await HandleEndpoint.dislike_tweet_by_id(
            api_key=invalid_data_to_dislike_tweet["api_key"],
            tweet_id=invalid_data_to_dislike_tweet["tweet_id"],
        )
        assert (
                result[0].keys()
                == invalid_data_to_dislike_tweet["result"][0].keys()
        )
        assert result[1] == invalid_data_to_dislike_tweet["result"][1]
        assert len(result) == len(invalid_data_to_dislike_tweet["result"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_like_tweet_by_id(init_test_data_for_db: None) -> None:
        result = await HandleEndpoint.like_tweet_by_id(
            api_key=valid_data_to_like_tweet["api_key"],
            tweet_id=valid_data_to_like_tweet["tweet_id"],
        )
        assert result == valid_data_to_like_tweet["result"]
        result = await HandleEndpoint.like_tweet_by_id(
            api_key=invalid_data_to_like_tweet["api_key"],
            tweet_id=invalid_data_to_like_tweet["tweet_id"],
        )
        assert (
                result[0].keys()
                == invalid_data_to_like_tweet["result"][0].keys()
        )
        assert result[1] == invalid_data_to_like_tweet["result"][1]
        assert len(result) == len(invalid_data_to_like_tweet["result"])

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
                user_profile == CORRECT_GET_USER_PROFILE_RESPONSE[
            "user_profile"]
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
        api_key = CORRECT_GET_OWN_PROFILE_RESPONSE["own_profile"]["user"][
            "name"
        ]
        own_profile, http_status_code = (
            await HandleEndpoint.get_own_profile_details(api_key)
        )
        assert own_profile == CORRECT_GET_OWN_PROFILE_RESPONSE["own_profile"]
        assert (
                http_status_code
                == CORRECT_GET_OWN_PROFILE_RESPONSE["http_status_code"]
        )

        api_key = invalid_data_get_own_profile["api_key"]
        error_message, http_status_code = (
            await HandleEndpoint.get_own_profile_details(api_key)
        )
        expected_message = invalid_data_get_own_profile["result"]["message"]
        expected_http_status_code = (
            invalid_data_get_own_profile["result"]["http_status_code"]
        )
        assert error_message.keys() == expected_message.keys()
        assert expected_message["result"] == expected_message["result"]
        assert http_status_code == expected_http_status_code

    @staticmethod
    @pytest_mark.asyncio
    async def test_follow_other_user(init_test_data_for_db: None) -> None:
        message, http_status_code = await HandleEndpoint.follow_other_user(
            api_key=user_can_follow_user["api_key"],
            followed_id=user_can_follow_user["followed_id"],
        )
        expected_result = user_can_follow_user["result"]
        assert message == expected_result["message"]
        assert http_status_code == expected_result["http_status_code"]
        message, http_status_code = await HandleEndpoint.follow_other_user(
            api_key=user_cannot_follow_user["api_key"],
            followed_id=user_cannot_follow_user["followed_id"],
        )
        expected_result = user_cannot_follow_user["result"]
        assert http_status_code == expected_result["http_status_code"]
        assert (
                message.get("result", None) == expected_result["message"][
            "result"]
        )
        assert message.keys() == expected_result["message"].keys()
        assert isinstance(message.get("error_type", None), str)
        assert isinstance(message.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_unfollow_other_user(init_test_data_for_db: None) -> None:
        message, http_status_code = await HandleEndpoint.unfollow_user(
            api_key=user_can_unfollow_user["api_key"],
            followed_id=user_can_unfollow_user["followed_id"],
        )
        expected_result = user_can_unfollow_user["result"]
        assert message == expected_result["message"]
        assert http_status_code == expected_result["http_status_code"]
        message, http_status_code = await HandleEndpoint.unfollow_user(
            api_key=user_cannot_unfollow_user["api_key"],
            followed_id=user_cannot_unfollow_user["followed_id"],
        )
        expected_result = user_cannot_unfollow_user["result"]
        assert http_status_code == expected_result["http_status_code"]
        assert (
                message.get("result", None) == expected_result["message"][
            "result"]
        )
        assert message.keys() == expected_result["message"].keys()
        assert isinstance(message.get("error_type", None), str)
        assert isinstance(message.get("error_message", None), str)
