from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CORRECT_GET_USER_PROFILE_RESPONSE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
)

get_user_profile_endpoint = FAKE_TWITTER_ENDPOINTS["get_user_profile"][
    "endpoint"
]
GET_USER_PROFILE_HTTP_METHOD = FAKE_TWITTER_ENDPOINTS["get_user_profile"][
    "http_method"
]
exist_user_id = CORRECT_GET_USER_PROFILE_RESPONSE["user_profile"]["user"]["id"]
unexist_user_id = 0


class TestGetUserProfileEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_if_user_not_existed(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        response = await client.request(
            method=GET_USER_PROFILE_HTTP_METHOD,
            url=get_user_profile_endpoint.format(id=unexist_user_id),
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
            method=GET_USER_PROFILE_HTTP_METHOD,
            url=get_user_profile_endpoint.format(id=exist_user_id),
            headers=AUTHORIZED_HEADER,
        )
        own_profile = response.json()
        assert own_profile == CORRECT_GET_USER_PROFILE_RESPONSE["user_profile"]
        assert (
            response.status_code
            == CORRECT_GET_USER_PROFILE_RESPONSE["http_status_code"]
        )
