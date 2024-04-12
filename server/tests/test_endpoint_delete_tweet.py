from os import listdir as os_listdir

from pytest import mark as pytest_mark
from httpx import AsyncClient

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    FORBIDDEN_STATUS_CODE,
    delete_tweet_endpoint,
    ERROR_MESSAGE,
    SAVE_MEDIA_ABS_PATH,
    TWEET_1,
    TWEET_2,
    TWEET_3

)
from server.app.database import Tweet

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
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        for i_endpoint in INVALID_DELETE_TWEET_ENDPOINTS:
            response = await client.delete(
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
            response = await client.delete(
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
        response = await client.delete(
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
        await client.delete(
                url=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[1][0],
                headers=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[1][1]
            )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    # @staticmethod
    # @pytest_mark.asyncio
    # async def test_endpoint_that_tweet_media_file_deleted_from_db(
    #         client: AsyncClient,
    #         init_test_data_for_db: None,
    #         init_midia_file_for_test: None) -> None:
    #     await client.delete(
    #             url=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[0][0],
    #             headers=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[0][1]
    #         )
    #
    #
    # @staticmethod
    # @pytest_mark.asyncio
    # async def test_endpoint_that_tweet_deleted_from_db(
    #         client: AsyncClient,
    #         init_test_data_for_db: None,
    #         init_midia_file_for_test: None) -> None:
    #     await client.delete(
    #             url=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[0][0],
    #             headers=VALID_DELETE_TWEET_ENDPOINTS_AND_HEADER[0][1]
    #         )



    # @staticmethod
    # @pytest_mark.asyncio
    # async def test_endpoint_that_tweet_added_in_db(
    #         client: AsyncClient,
    #         init_test_data_for_db: None, ) -> None:
    #     total_tweets_before = await Tweet.get_total_tweets()
    #     await client.post(
    #         url=ADD_TWEET_ENDPOINT,
    #         headers=AUTHORIZED_HEADER,
    #         json=CORRECT_TWEET_BODY_DATA_AND_RESPONSE[0][0]
    #     )
    #     total_tweets_after = await Tweet.get_total_tweets()
    #     assert total_tweets_before + 1 == total_tweets_after
