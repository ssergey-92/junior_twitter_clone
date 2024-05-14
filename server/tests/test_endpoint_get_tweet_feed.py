"""Module for testing endpoint 'get tweet feed' from app.routes.py ."""
from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    CORRECT_GET_TWEET_FEED_RESPONSE,
    APPLICATION_ENDPOINTS,
)


class TestGetTweetFeedEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=APPLICATION_ENDPOINTS["get_tweet_feed"]["http_method"],
            url=APPLICATION_ENDPOINTS["get_tweet_feed"]["endpoint"],
            headers=AUTHORIZED_HEADER,
        )
        assert response.json() == CORRECT_GET_TWEET_FEED_RESPONSE["tweet_feed"]
        assert (response.status_code ==
                CORRECT_GET_TWEET_FEED_RESPONSE["status_code"])
