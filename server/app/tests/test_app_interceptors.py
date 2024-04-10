from pytest import mark as pytest_park
from httpx import AsyncClient

POST_APP_ROUTES_FOR_TESTING = [
    "/api/tweets",
    "/api/medias",
    "/api/is_not_existed",  # Url is not existed
    "/api/tweets/1"  # Has DELETE method only
    # ("/api/tweets/1", "DELETE"),
    # ("/api/tweets/1/likes", "POST"),
    # "/api/tweets/1/likes",
    # "/api/users/1/follow",
    # "api/users/1/follow",
    # "/api/tweets",
    # "/api/users/me",
    # "/api/users/1"
]
ERROR_MESSAGE = {
    "result": False,
    "error_type": "",
    "error_message": ""
}

UNAUTHORIZED_HEADERS = [{"api-key": "not_existed"}, {}]
UNAUTHORIZED_SATUS_CODE = 401
AUTHORIZED_HEADER = {"api-key": "test_1"}
AUTHORIZED_SATUS_CODE = 200


class TestAppInterceptors:

    @staticmethod
    @pytest_park.asyncio
    async def test_intercept_request_unauthorized(
            client: AsyncClient,
            init_test_data: None) -> None:
        for i_data in UNAUTHORIZED_HEADERS:
            for i_url in POST_APP_ROUTES_FOR_TESTING:
                response = await client.post(url=i_url, headers=i_data)
                response_data = response.json()
                assert response.status_code == UNAUTHORIZED_SATUS_CODE
                assert response_data.keys() == ERROR_MESSAGE.keys()
                assert response_data.get("result", None) == \
                       ERROR_MESSAGE["result"]
                assert isinstance(response_data.get("error_type", None), str)
                assert isinstance(
                    response_data.get("error_message", None), str
                )

    @staticmethod
    @pytest_park.asyncio
    async def test_intercept_request_authorized(
            client: AsyncClient,
            init_test_data: None) -> None:
        for i_url in POST_APP_ROUTES_FOR_TESTING:
            response = await client.get(url=i_url, headers=AUTHORIZED_HEADER)
            assert response.status_code != 401

