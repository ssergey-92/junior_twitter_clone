"""Module for testing endpoint 'get user profile' from app.routes.py ."""
from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CORRECT_GET_USER_PROFILE_RESPONSE,
    ERROR_MESSAGE,
    APPLICATION_ENDPOINTS,
)

get_user_profile_url = APPLICATION_ENDPOINTS["get_user_profile"]["endpoint"]
get_user_profile_method = (
    APPLICATION_ENDPOINTS["get_user_profile"]["http_method"])
exist_user_id = CORRECT_GET_USER_PROFILE_RESPONSE["profile"]["user"]["id"]
unexist_user_id = 0


class TestGetUserProfileEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_if_user_not_existed(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=get_user_profile_method,
            url=get_user_profile_url.format(id=unexist_user_id),
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
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=get_user_profile_method,
            url=get_user_profile_url.format(id=exist_user_id),
            headers=AUTHORIZED_HEADER,
        )
        own_profile = response.json()
        assert own_profile == CORRECT_GET_USER_PROFILE_RESPONSE["profile"]
        assert (response.status_code ==
                CORRECT_GET_USER_PROFILE_RESPONSE["status_code"])
