from httpx import AsyncClient
from pytest import mark as pytest_mark

from ..app.database import TweetLike
from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
)

dislike_tweet_endpoint = FAKE_TWITTER_ENDPOINTS["dislike_tweet"]["endpoint"]
DISLIKE_TWEET_HTTP_METHOD = (FAKE_TWITTER_ENDPOINTS)["dislike_tweet"][
    "http_method"
]
INVALID_DISLIKE_TWEET_ENDPOINTS = (
    dislike_tweet_endpoint.format(id="ten"),
    dislike_tweet_endpoint.format(id=()),
)
USER_CAN_DISLIKE_TWEET = {"user_header": AUTHORIZED_HEADER, "tweet_id": 1}
USER_CANNOT_DISLIKE_TWEET = {"user_header": AUTHORIZED_HEADER, "tweet_id": 2}
CORRECT_DISLIKE_TWEET_RESPONSE = {"result": True}


class TestDislikeTweetEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
        client: AsyncClient,
    ) -> None:
        for i_endpoint in INVALID_DISLIKE_TWEET_ENDPOINTS:
            response = await client.request(
                method=DISLIKE_TWEET_HTTP_METHOD,
                url=i_endpoint,
                headers=AUTHORIZED_HEADER,
            )
            response_data = response.json()
            assert response.status_code == BAD_REQUEST_STATUS_CODE
            assert response_data.get("result", None) == ERROR_MESSAGE["result"]
            assert response_data.keys() == ERROR_MESSAGE.keys()
            assert isinstance(response_data.get("error_type", None), str)
            assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        response = await client.request(
            method=DISLIKE_TWEET_HTTP_METHOD,
            url=dislike_tweet_endpoint.format(
                id=USER_CAN_DISLIKE_TWEET["tweet_id"]
            ),
            headers=USER_CAN_DISLIKE_TWEET["user_header"],
        )
        assert response.json() == CORRECT_DISLIKE_TWEET_RESPONSE
        assert response.status_code == 201

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_user_can_not_dislike_not_liked_tweet(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        response = await client.request(
            method=DISLIKE_TWEET_HTTP_METHOD,
            url=dislike_tweet_endpoint.format(
                id=USER_CANNOT_DISLIKE_TWEET["tweet_id"]
            ),
            headers=USER_CANNOT_DISLIKE_TWEET["user_header"],
        )
        response_data = response.json()
        assert response.status_code == BAD_REQUEST_STATUS_CODE
        assert response_data.get("result", None) == ERROR_MESSAGE["result"]
        assert response_data.keys() == ERROR_MESSAGE.keys()
        assert isinstance(response_data.get("error_type", None), str)
        assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_like_removed_from_db(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        total_likes_before = await TweetLike.get_total_likes()
        response = await client.request(
            method=DISLIKE_TWEET_HTTP_METHOD,
            url=dislike_tweet_endpoint.format(
                id=USER_CAN_DISLIKE_TWEET["tweet_id"]
            ),
            headers=USER_CAN_DISLIKE_TWEET["user_header"],
        )
        total_likes_after = await TweetLike.get_total_likes()
        assert total_likes_after == total_likes_before - 1
