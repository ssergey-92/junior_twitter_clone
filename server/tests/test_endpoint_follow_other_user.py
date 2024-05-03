from httpx import AsyncClient
from pytest import mark as pytest_mark

from ..app.database import User
from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS
)

follow_user_endpoint = FAKE_TWITTER_ENDPOINTS["follow_user"]["endpoint"]
FOLLOW_USER_HTTP_METHOD = FAKE_TWITTER_ENDPOINTS["follow_user"]["http_method"]
INVALID_FOLLOW_USER_ENDPOINTS = (
    follow_user_endpoint.format(id="ten"),
    follow_user_endpoint.format(id=())
)
USER_CAN_FOLLOW_USER = {
    "user_header": AUTHORIZED_HEADER,
    "followed_user_id": 3
}
USER_FOLLOWED_USER = {"user_header": AUTHORIZED_HEADER, "followed_user_id": 2}
CORRECT_FOLLOW_USER_RESPONSE = {"result": True}


class TestFollowOtherUserEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
            client: AsyncClient) -> None:
        for i_endpoint in INVALID_FOLLOW_USER_ENDPOINTS:
            response = await client.request(
                method=FOLLOW_USER_HTTP_METHOD,
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
            init_test_data_for_db: None) -> None:
        response = await client.request(
            method=FOLLOW_USER_HTTP_METHOD,
            url=follow_user_endpoint.format(
                id=USER_CAN_FOLLOW_USER["followed_user_id"]
            ),
            headers=USER_CAN_FOLLOW_USER["user_header"]
            )
        assert response.json() == CORRECT_FOLLOW_USER_RESPONSE
        assert response.status_code == 201

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_user_can_not_follow_user_two_times(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        response = await client.request(
            method=FOLLOW_USER_HTTP_METHOD,
            url=follow_user_endpoint.format(
                id=USER_FOLLOWED_USER["followed_user_id"]
            ),
            headers=USER_FOLLOWED_USER["user_header"]
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
    async def test_that_followed_details_inserted_in_db(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        total_followed_before = await User.get_total_followed_by_name(
            AUTHORIZED_HEADER["api-key"]
        )
        response = await client.request(
            method=FOLLOW_USER_HTTP_METHOD,
            url=follow_user_endpoint.format(
                id=USER_CAN_FOLLOW_USER["followed_user_id"]
            ),
            headers=USER_CAN_FOLLOW_USER["user_header"]
            )
        total_followed_after = await User.get_total_followed_by_name(
            AUTHORIZED_HEADER["api-key"]
        )
        assert total_followed_before + 1 == total_followed_after
