"""Module for testing endpoint 'add tweet' app.fastapi_app.py ."""

from httpx import AsyncClient
from pytest import mark as pytest_mark

from app.models.tweets import Tweet

from .common import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    APPLICATION_ENDPOINTS,
)

add_tweet_endpoint = APPLICATION_ENDPOINTS["add_tweet"]["endpoint"]
add_tweet_http_method = APPLICATION_ENDPOINTS["add_tweet"]["http_method"]
correct_tweet_body_data_and_response = (
    {
        "body": {"tweet_data": "tweet # 4"},
        "result": {
            "message": {"result": True, "tweet_id": 4},
            "status_code": CREATED_STATUS_CODE,
        },
    },
    {
        "body": {"tweet_data": "tweet # 5", "tweet_media_ids": None},
        "result": {
            "message": {"result": True, "tweet_id": 5},
            "status_code": CREATED_STATUS_CODE,
        },
    },
    {
        "body": {"tweet_data": "tweet # 6", "tweet_media_ids": [1, 2]},
        "result": {
            "message": {"result": True, "tweet_id": 6},
            "status_code": CREATED_STATUS_CODE,
        },
    },
)
incorrect_tweet_body_data = {
    "body": (
        {"tweet_data": 123},
        {"tweet_media_ids": [1, 3]},
        {"tweet_data": "str", "tweet_media_ids": [1, "number"]},
    ),
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}


class TestAddTweetEndpoint:
    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_request_body(
        client: AsyncClient,
    ) -> None:
        for i_body in incorrect_tweet_body_data["body"]:
            response = await client.request(
                method=add_tweet_http_method,
                url=add_tweet_endpoint,
                headers=AUTHORIZED_HEADER,
                json=i_body,
            )
            response_data = response.json()
            assert (response.status_code ==
                    incorrect_tweet_body_data["result"]["status_code"])
            assert (response_data.keys() ==
                    incorrect_tweet_body_data["result"]["message"].keys())
            assert (response_data["result"] ==
                    incorrect_tweet_body_data["result"]["message"]["result"])
            assert isinstance(response_data["error_type"], str)
            assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient,
        init_test_data_for_db: None,
    ) -> None:
        for i_data in correct_tweet_body_data_and_response:
            response = await client.request(
                method=add_tweet_http_method,
                url=add_tweet_endpoint,
                headers=AUTHORIZED_HEADER,
                json=i_data["body"],
            )
            assert response.json() == i_data["result"]["message"]
            assert response.status_code == i_data["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_tweet_added_in_db(
        client: AsyncClient,
        init_test_data_for_db: None,
    ) -> None:
        total_tweets_before = await Tweet.get_total_tweets()
        await client.request(
            method=add_tweet_http_method,
            url=add_tweet_endpoint,
            headers=AUTHORIZED_HEADER,
            json=correct_tweet_body_data_and_response[0]["body"],
        )
        total_tweets_after = await Tweet.get_total_tweets()
        assert total_tweets_before + 1 == total_tweets_after
