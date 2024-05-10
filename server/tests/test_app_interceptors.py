"""Module for testing app interceptors  from app.routes.py ."""
from httpx import AsyncClient
from pytest import mark as pytest_mark
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    DEFAULT_TABLE_NAMES,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
    UNAUTHORIZED_SATUS_CODE,
)

delete_tweet_endpoint = FAKE_TWITTER_ENDPOINTS["delete_tweet"]["endpoint"]
test_routes_for_intercept_requests = (
    {
        "endpoint": FAKE_TWITTER_ENDPOINTS["add_media"]["endpoint"],
        "http_method": FAKE_TWITTER_ENDPOINTS["add_media"]["http_method"],
        "result": {
            "message": ERROR_MESSAGE, "status_code": UNAUTHORIZED_SATUS_CODE,
        },
    },
    {
        "endpoint": "/api/url_is_not_existed",  # Url is not existed
        "http_method": "GET",
        "result": {
            "message": ERROR_MESSAGE, "status_code": UNAUTHORIZED_SATUS_CODE,
        },
    },
    {
        "endpoint": delete_tweet_endpoint.format(id=1),
        "http_method": FAKE_TWITTER_ENDPOINTS["delete_tweet"]["http_method"],
        "result": {
            "message": ERROR_MESSAGE, "status_code": UNAUTHORIZED_SATUS_CODE,
        },
    },
)
test_routes_for_http_exception_handler = (
    {
        "endpoint": "/api/url_is_not_existed",  # Url is not existed
        "http_method": "GET",
        "result": {"message": ERROR_MESSAGE},
    },
    {
        "endpoint": delete_tweet_endpoint.format(id=1),
        "http_method": "PUT",  # HAS DELETE METHOD ONLY
        "result": {"message": ERROR_MESSAGE},
    },
)
unauthorized_headers: tuple = ({"api-key": "not_existed"}, {})


class TestAppInterceptors:

    @staticmethod
    @pytest_mark.asyncio
    async def test_intercept_request_unauthorized(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        for i_header in unauthorized_headers:
            for i_data in test_routes_for_intercept_requests:
                response = await client.request(
                    method=i_data["http_method"],
                    url=i_data["endpoint"],
                    headers=i_header,
                )
                response_data = response.json()
                assert response.status_code == i_data["result"]["status_code"]
                assert (response_data.keys() ==
                        i_data["result"]["message"].keys())
                assert response_data["result"] == ERROR_MESSAGE["result"]
                assert isinstance(response_data["error_type"], str)
                assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_http_exception_handler(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        for i_data in test_routes_for_http_exception_handler:
            response = await client.request(
                method=i_data["http_method"],
                url=i_data["endpoint"],
                headers=AUTHORIZED_HEADER,
            )
            response_data = response.json()
            assert response_data.keys() == i_data["result"]["message"].keys()
            assert response_data["result"] == ERROR_MESSAGE["result"]
            assert isinstance(response_data["error_type"], str)
            assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_lifespan(app: None, test_session: AsyncSession) -> None:
        table_names_query = await test_session.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public';",
            ),
        )
        table_names = table_names_query.scalars().fetchall()
        sorted_table_names = sorted(table_names)
        assert sorted_table_names == DEFAULT_TABLE_NAMES
