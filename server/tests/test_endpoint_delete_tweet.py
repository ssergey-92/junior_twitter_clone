from os import listdir as os_listdir

from pytest import mark as pytest_mark
from httpx import AsyncClient

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
    FORBIDDEN_STATUS_CODE,
    SAVE_MEDIA_ABS_PATH,
    TWEET_1,
    TWEET_2,
    TWEET_3

)
from server.app.database import MediaFile, Tweet, TweetLike

delete_tweet_endpoint = FAKE_TWITTER_ENDPOINTS["delete_tweet"]["endpoint"]
DELETE_TWEET_HTTP_METHOD = FAKE_TWITTER_ENDPOINTS["delete_tweet"]["http_method"]
INVALID_DELETE_TWEET_ENDPOINTS = (
    delete_tweet_endpoint.format(id='ten'),
    delete_tweet_endpoint.format(id=()),
    delete_tweet_endpoint.format(id={"key": "value"})
)
VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER = (
    (delete_tweet_endpoint.format(id=1), {"api-key": TWEET_1["author_name"]}),
    (delete_tweet_endpoint.format(id=2), {"api-key": TWEET_2["author_name"]}),
    (delete_tweet_endpoint.format(id=3), {"api-key": TWEET_3["author_name"]})
)
DELETE_NOT_OWN_TWEET_ENDPOINT_AND_HEADER = (
    delete_tweet_endpoint.format(id=1), {"api-key": TWEET_2["author_name"]}
)
CORRECT_DELETE_TWEET_RESPONSE = {"result": True}


class TestDeleteTweetEndpoint:
    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
            client: AsyncClient) -> None:
        for i_endpoint in INVALID_DELETE_TWEET_ENDPOINTS:
            response = await client.request(
                method=DELETE_TWEET_HTTP_METHOD,
                url=i_endpoint,
                headers=AUTHORIZED_HEADER
            )
            response_data = response.json()
            assert response.status_code == BAD_REQUEST_STATUS_CODE
            assert response_data.get("result", None) == \
                   ERROR_MESSAGE["result"]
            assert response_data.keys() == ERROR_MESSAGE.keys()
            assert isinstance(response_data.get("error_type", None), str)
            assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
            client: AsyncClient,
            init_test_data_for_db: None,
            init_midia_file_for_test: None) -> None:
        for i_data in VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER:
            response = await client.request(
                method=DELETE_TWEET_HTTP_METHOD,
                url=i_data[0],
                headers=i_data[1]
            )
            assert response.json() == CORRECT_DELETE_TWEET_RESPONSE
            assert response.status_code == 200

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_user_can_delete_only_own_tweet(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        response = await client.request(
                method=DELETE_TWEET_HTTP_METHOD,
                url=DELETE_NOT_OWN_TWEET_ENDPOINT_AND_HEADER[0],
                headers=DELETE_NOT_OWN_TWEET_ENDPOINT_AND_HEADER[1]
            )
        response_data = response.json()
        assert response.status_code == FORBIDDEN_STATUS_CODE
        assert response_data.get("result", None) == ERROR_MESSAGE["result"]
        assert response_data.keys() == ERROR_MESSAGE.keys()
        assert isinstance(response_data.get("error_type", None), str)
        assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_tweet_media_file_deleted_from_sys(
            client: AsyncClient,
            init_test_data_for_db: None,
            init_midia_file_for_test: None) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await client.request(
                method=DELETE_TWEET_HTTP_METHOD,
                url=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[1][0],
                headers=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[1][1]
            )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))

        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_tweet_details_deleted_from_db(
            client: AsyncClient,
            init_test_data_for_db: None,
            init_midia_file_for_test: None) -> None:

        total_tweets_before = await Tweet.get_total_tweets()
        total_media_before = await MediaFile.get_total_media_files()
        total_likes_before = await TweetLike.get_total_likes()
        await client.request(
                method=DELETE_TWEET_HTTP_METHOD,
                url=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[1][0],
                headers=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[1][1]
            )
        total_tweets_after = await Tweet.get_total_tweets()
        total_media_after = await MediaFile.get_total_media_files()
        total_likes_after = await TweetLike.get_total_likes()

        assert total_tweets_before - 1 == total_tweets_after
        assert total_media_before - 2 == total_media_after
        assert total_likes_before - 2 == total_likes_after
