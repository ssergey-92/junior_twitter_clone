from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    CORRECT_GET_TWEET_FEED_RESPONSE,
    FAKE_TWITTER_ENDPOINTS,
    OK_STATUS_CODE,
)


class TestGetTweetFeedEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        response = await client.request(
            method=FAKE_TWITTER_ENDPOINTS["get_tweet_feed"]["http_method"],
            url=FAKE_TWITTER_ENDPOINTS["get_tweet_feed"]["endpoint"],
            headers=AUTHORIZED_HEADER,
        )
        tweet_feed = response.json()
        assert tweet_feed == CORRECT_GET_TWEET_FEED_RESPONSE["tweet_feed"]
        assert (
            response.status_code
            == CORRECT_GET_TWEET_FEED_RESPONSE["http_status_code"]
        )
