from pytest import mark as pytest_mark
from httpx import AsyncClient

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    ADD_TWEET_ENDPOINT
)
from server.app.database import Tweet


CORRECT_TWEET_BODY_DATA_AND_RESPONSE = [
    ({"tweet_data": "tweet # 4"}, {"result": True, "tweet_id": 4}),
    ({"tweet_data": "tweet # 5", "tweet_media_ids": None},
     {"result": True, "tweet_id": 5}),
    ({"tweet_data": "tweet # 6", "tweet_media_ids": [1, 2]},
     {"result": True, "tweet_id": 6}),
]
INCORRECT_TWEET_BODY_DATA = [
    {},
    {"tweet_data": 123},
    {"tweet_media_ids": [1, 3]},
    {"tweet_data": "str", "tweet_media_ids": [1, "number"]}
]


class TestAddTweetEndpoint:
    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_request_body(
            client: AsyncClient) -> None:
        for i_data in INCORRECT_TWEET_BODY_DATA:
            response = await client.post(
                url=ADD_TWEET_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                json=i_data
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
            client: AsyncClient,
            init_test_data_for_db: None, ) -> None:
        for i_data in CORRECT_TWEET_BODY_DATA_AND_RESPONSE:
            response = await client.post(
                url=ADD_TWEET_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                json=i_data[0]
            )
            assert response.json() == i_data[1]
            assert response.status_code == CREATED_STATUS_CODE

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_tweet_added_in_db(
            client: AsyncClient,
            init_test_data_for_db: None, ) -> None:
        total_tweets_before = await Tweet.get_total_tweets()
        await client.post(
                url=ADD_TWEET_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                json=CORRECT_TWEET_BODY_DATA_AND_RESPONSE[0][0]
            )
        total_tweets_after = await Tweet.get_total_tweets()
        assert total_tweets_before + 1 == total_tweets_after
