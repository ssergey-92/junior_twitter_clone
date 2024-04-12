from pytest import mark as pytest_mark
from httpx import AsyncClient

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    ERROR_MESSAGE,
    METHOD_NOT_ALLOWED_SATUS_CODE,
    NOT_FOUND_SATUS_CODE,
    UNAUTHORIZED_SATUS_CODE
)

TEST_ROUTES_FOR_INTERCEPT_REQUESTS = [
    "/api/medias",  # Has "POST" method
    "/api/url_is_not_existed",  # Url is not existed
    "/api/tweets/1"  # Has "DELETE" method only
]
TEST_ROUTES_FOR_HTTP_EXCEPTION_HANDLER = [
    "/api/url_is_not_existed",  # Url is not existed
    "/api/tweets/1"  # Has "DELETE" method only
]
UNAUTHORIZED_HEADERS = [{"api-key": "not_existed"}, {}]


class TestAppInterceptors:

    @staticmethod
    @pytest_mark.asyncio
    async def test_intercept_request_unauthorized(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        for i_data in UNAUTHORIZED_HEADERS:
            for i_url in TEST_ROUTES_FOR_INTERCEPT_REQUESTS:
                response = await client.post(url=i_url, headers=i_data)
                response_data = response.json()
                assert response.status_code == UNAUTHORIZED_SATUS_CODE
                assert (response_data.get("result", None) ==
                        ERROR_MESSAGE["result"])
                assert response_data.keys() == ERROR_MESSAGE.keys()
                assert isinstance(response_data.get("error_type", None), str)
                assert isinstance(
                    response_data.get("error_message", None), str
                )

    @staticmethod
    @pytest_mark.asyncio
    async def test_intercept_request_authorized(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        for i_url in TEST_ROUTES_FOR_INTERCEPT_REQUESTS:
            response = await client.get(url=i_url, headers=AUTHORIZED_HEADER)
            assert response.status_code != UNAUTHORIZED_SATUS_CODE

    @staticmethod
    @pytest_mark.asyncio
    async def test_http_exception_handler(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:

        # work after passing authorization

        for i_url in TEST_ROUTES_FOR_HTTP_EXCEPTION_HANDLER:
            response = await client.get(url=i_url, headers=AUTHORIZED_HEADER)
            response_data = response.json()
            assert response_data.keys() == ERROR_MESSAGE.keys()
            assert response_data.get("result", None) == ERROR_MESSAGE["result"]
            assert isinstance(response_data.get("error_type", None), str)
            assert isinstance(response_data.get("error_message", None), str)

    # validation exception handler is tested per each endpoint independently
