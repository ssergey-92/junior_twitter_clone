"""Module for testing endpoint 'delete tweet' from app.routes.py ."""
from os import listdir as os_listdir

from httpx import AsyncClient
from pytest import mark as pytest_mark

from server.app.database import MediaFile, Tweet, TweetLike

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    APPLICATION_ENDPOINTS,
    FORBIDDEN_STATUS_CODE,
    SAVE_MEDIA_ABS_PATH,
    TWEET_1,
    TWEET_2,
    TWEET_3,
)

delete_tweet_endpoint = APPLICATION_ENDPOINTS["delete_tweet"]["endpoint"]
delete_tweet_http_method = APPLICATION_ENDPOINTS["delete_tweet"]["http_method"]
invalid_delete_tweet_data_1 = {
    "urls": (
            delete_tweet_endpoint.format(id="ten"),
            delete_tweet_endpoint.format(id=()),
            delete_tweet_endpoint.format(id={"key": "value"}),
    ),
    "header": AUTHORIZED_HEADER,
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}
valid_delete_tweet_data = {
    "data": (
        {
            "url": delete_tweet_endpoint.format(id=1),
            "header": {"api-key": TWEET_1["author_name"]},
        },
        {
            "url": delete_tweet_endpoint.format(id=2),
            "header": {"api-key": TWEET_2["author_name"]},
        },
        {
            "url": delete_tweet_endpoint.format(id=3),
            "header": {"api-key": TWEET_3["author_name"]},
        },
    ),
    "result": {
        "message": {"result": True}, "status_code": CREATED_STATUS_CODE
    },
}
invalid_delete_tweet_data_2 = {
    "url": delete_tweet_endpoint.format(id=1),  # tweet is not belong to user
    "header": {"api-key": TWEET_2["author_name"]},
    "result": {"message": ERROR_MESSAGE, "status_code": FORBIDDEN_STATUS_CODE},
}


class TestDeleteTweetEndpoint:
    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
        client: AsyncClient,
    ) -> None:
        for i_url in invalid_delete_tweet_data_1["urls"]:
            response = await client.request(
                method=delete_tweet_http_method,
                url=i_url,
                headers=invalid_delete_tweet_data_1["header"],
            )
            response_data = response.json()
            expected_message = invalid_delete_tweet_data_1["result"]["message"]
            assert (response.status_code ==
                    invalid_delete_tweet_data_1["result"]["status_code"])
            assert response_data.keys() == expected_message.keys()
            assert response_data["result"] == expected_message["result"]
            assert isinstance(response_data["error_type"], str)
            assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        for i_data in valid_delete_tweet_data["data"]:
            response = await client.request(
                method=delete_tweet_http_method,
                url=i_data["url"],
                headers=i_data["header"],
            )
            assert (response.json() ==
                    valid_delete_tweet_data["result"]["message"])
            assert (response.status_code ==
                    valid_delete_tweet_data["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_user_can_delete_only_own_tweet(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=delete_tweet_http_method,
            url=invalid_delete_tweet_data_2["url"],
            headers=invalid_delete_tweet_data_2["header"],
        )
        response_data = response.json()
        assert (response.status_code ==
                invalid_delete_tweet_data_2["result"]["status_code"])
        assert (response_data.keys() ==
                invalid_delete_tweet_data_2["result"]["message"].keys())
        assert (response_data["result"] ==
                invalid_delete_tweet_data_2["result"]["message"]["result"])
        assert isinstance(response_data["error_type"], str)
        assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_tweet_media_file_deleted_from_sys(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await client.request(
            method=delete_tweet_http_method,
            url=valid_delete_tweet_data["data"][1]["url"],
            headers=valid_delete_tweet_data["data"][1]["header"],
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_tweet_details_deleted_from_db(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        total_tweets_before = await Tweet.get_total_tweets()
        total_media_before = await MediaFile.get_total_media_files()
        total_likes_before = await TweetLike.get_total_likes()
        await client.request(
            method=delete_tweet_http_method,
            url=valid_delete_tweet_data["data"][1]["url"],
            headers=valid_delete_tweet_data["data"][1]["header"],
        )
        total_tweets_after = await Tweet.get_total_tweets()
        total_media_after = await MediaFile.get_total_media_files()
        total_likes_after = await TweetLike.get_total_likes()
        assert total_tweets_before - 1 == total_tweets_after
        assert total_media_before - 2 == total_media_after
        assert total_likes_before - 2 == total_likes_after
