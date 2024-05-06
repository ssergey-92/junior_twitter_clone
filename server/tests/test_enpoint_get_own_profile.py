from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    CORRECT_GET_OWN_PROFILE_RESPONSE,
    FAKE_TWITTER_ENDPOINTS)


class TestGetOwnProfileEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        apy_key = \
            CORRECT_GET_OWN_PROFILE_RESPONSE["own_profile"]["user"]["name"]
        response = await client.request(
            method=FAKE_TWITTER_ENDPOINTS["get_own_profile"]["http_method"],
            url=FAKE_TWITTER_ENDPOINTS["get_own_profile"]["endpoint"],
            headers={"api-key": apy_key}
        )
        own_profile = response.json()
        assert (own_profile ==
                CORRECT_GET_OWN_PROFILE_RESPONSE["own_profile"])
        assert (response.status_code ==
                CORRECT_GET_OWN_PROFILE_RESPONSE["http_status_code"])
