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
TEST_ROUTES_FOR_INTERCEPT_REQUESTS = [
    {
        "endpoint": FAKE_TWITTER_ENDPOINTS["add_media"]["endpoint"],
        "http_method": FAKE_TWITTER_ENDPOINTS["add_media"]["http_method"],
    },
    {
        "endpoint": "/api/url_is_not_existed",  # Url is not existed
        "http_method": "GET",
    },
    {
        "endpoint": delete_tweet_endpoint.format(id=1),
        "http_method": FAKE_TWITTER_ENDPOINTS["delete_tweet"]["http_method"],
    },
]
TEST_ROUTES_FOR_HTTP_EXCEPTION_HANDLER = [
    {
        "endpoint": "/api/url_is_not_existed",  # Url is not existed
        "http_method": "GET",
    },
    {
        "endpoint": delete_tweet_endpoint.format(id=1),
        "http_method": "PUT",  # HAS DELETE METHOD ONLY
    },
]
UNAUTHORIZED_HEADERS = [{"api-key": "not_existed"}, {}]


class TestAppInterceptors:

    @staticmethod
    @pytest_mark.asyncio
    async def test_intercept_request_unauthorized(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        for i_data in UNAUTHORIZED_HEADERS:
            for i_url in TEST_ROUTES_FOR_INTERCEPT_REQUESTS:
                response = await client.request(
                    method=i_url["http_method"],
                    url=i_url["endpoint"],
                    headers=i_data,
                )
                response_data = response.json()
                assert response.status_code == UNAUTHORIZED_SATUS_CODE
                assert (
                    response_data.get("result", None)
                    == ERROR_MESSAGE["result"]
                )
                assert response_data.keys() == ERROR_MESSAGE.keys()
                assert isinstance(response_data.get("error_type", None), str)
                assert isinstance(
                    response_data.get("error_message", None), str
                )

    @staticmethod
    @pytest_mark.asyncio
    async def test_http_exception_handler(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:

        # work after passing authorization

        for i_url in TEST_ROUTES_FOR_HTTP_EXCEPTION_HANDLER:
            response = await client.request(
                method=i_url["http_method"],
                url=i_url["endpoint"],
                headers=AUTHORIZED_HEADER,
            )
            response_data = response.json()
            assert response_data.keys() == ERROR_MESSAGE.keys()
            assert response_data.get("result", None) == ERROR_MESSAGE["result"]
            assert isinstance(response_data.get("error_type", None), str)
            assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_lifespan(
            app: None, test_session: AsyncSession,
    ) -> None:
        table_names_query = await test_session.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
            ),
        )
        table_names = table_names_query.scalars().fetchall()
        assert table_names == DEFAULT_TABLE_NAMES


