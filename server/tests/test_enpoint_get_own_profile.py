"""Module for testing endpoint 'get own profile' from app.routes.py ."""
from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    CORRECT_GET_OWN_PROFILE_RESPONSE,
    APPLICATION_ENDPOINTS,
)


class TestGetOwnProfileEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        apy_key = CORRECT_GET_OWN_PROFILE_RESPONSE["profile"]["user"]["name"]
        response = await client.request(
            method=APPLICATION_ENDPOINTS["get_own_profile"]["http_method"],
            url=APPLICATION_ENDPOINTS["get_own_profile"]["endpoint"],
            headers={"api-key": apy_key},
        )
        assert response.json() == CORRECT_GET_OWN_PROFILE_RESPONSE["profile"]
        assert (response.status_code ==
                CORRECT_GET_OWN_PROFILE_RESPONSE["status_code"])
