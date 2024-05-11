"""Module for testing endpoint 'like tweet' from app.routes.py ."""
from httpx import AsyncClient
from pytest import mark as pytest_mark

from ..app.database import TweetLike
from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
    test_user_1,
)

like_tweet_endpoint = FAKE_TWITTER_ENDPOINTS["like_tweet"]["endpoint"]
like_tweet_method = FAKE_TWITTER_ENDPOINTS["like_tweet"]["http_method"]
invalid_like_tweet_url = {
    "urls": (
        like_tweet_endpoint.format(id="ten"),
        like_tweet_endpoint.format(id=()),
    ),
    "header": AUTHORIZED_HEADER,
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}
user_can_like_tweet = {
    "header": {"api-key": test_user_1["name"]},
    "url": like_tweet_endpoint.format(id=2),
    "result": {
        "message": {"result": True}, "status_code": CREATED_STATUS_CODE,
    },
}
user_liked_tweet = {
    "header": {"api-key": test_user_1["name"]},
    "url": like_tweet_endpoint.format(id=1),
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}


class TestLikeTweetEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
        client: AsyncClient,
    ) -> None:
        for i_url in invalid_like_tweet_url["urls"]:
            response = await client.request(
                method=like_tweet_method,
                url=i_url,
                headers=invalid_like_tweet_url["header"],
            )
            response_data = response.json()
            expected_message = invalid_like_tweet_url["result"]["message"]
            assert (response.status_code ==
                    invalid_like_tweet_url["result"]["status_code"])
            assert response_data.keys() == expected_message.keys()
            assert response_data["result"] == expected_message["result"]
            assert isinstance(response_data["error_type"], str)
            assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=like_tweet_method,
            url=user_can_like_tweet["url"],
            headers=user_can_like_tweet["header"],
        )
        assert response.json() == user_can_like_tweet["result"]["message"]
        assert (response.status_code ==
                user_can_like_tweet["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_user_can_not_like_tweet_two_times(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=like_tweet_method,
            url=user_liked_tweet["url"],
            headers=user_liked_tweet["header"],
        )
        response_data = response.json()
        expected_message = user_liked_tweet["result"]["message"]
        assert (response.status_code ==
                user_liked_tweet["result"]["status_code"])
        assert response_data.keys() == expected_message.keys()
        assert response_data["result"] == expected_message["result"]
        assert isinstance(response_data["error_type"], str)
        assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_like_details_inserted_in_db(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        total_likes_before = await TweetLike.get_total_likes()
        await client.request(
            method=like_tweet_method,
            url=user_can_like_tweet["url"],
            headers=user_can_like_tweet["header"],
        )
        total_likes_after = await TweetLike.get_total_likes()
        assert total_likes_before + 1 == total_likes_after
