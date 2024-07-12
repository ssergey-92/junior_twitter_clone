"""Module for testing endpoint 'unfollow user' from app.fastapi_app.py ."""

from httpx import AsyncClient
from pytest import mark as pytest_mark

from app.models.users import User
from .common import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    APPLICATION_ENDPOINTS,
    test_user_1,
)

unfollow_user_endpoint = APPLICATION_ENDPOINTS["unfollow_user"]["endpoint"]
unfollow_user_method = APPLICATION_ENDPOINTS["unfollow_user"]["http_method"]
invalid_unfollow_user_data = {
    "urls": (
        unfollow_user_endpoint.format(id="ten"),
        unfollow_user_endpoint.format(id=()),
    ),
    "header": AUTHORIZED_HEADER,
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}
user_can_unfollow_user = {
    "user_name": test_user_1["name"],
    "url": unfollow_user_endpoint.format(id=2),
    "header": {"api-key": test_user_1["name"]},
    "result": {
        "message": {"result": True}, "status_code": CREATED_STATUS_CODE,
    },
}
user_not_following_user = {
    "url": unfollow_user_endpoint.format(id=3),
    "header": {"api-key": test_user_1["name"]},
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}


class TestUnfollowOtherUserEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
        client: AsyncClient,
    ) -> None:
        for i_url in invalid_unfollow_user_data["urls"]:
            response = await client.request(
                method=unfollow_user_method,
                url=i_url,
                headers=invalid_unfollow_user_data["header"],
            )
            response_data = response.json()
            expected_message = invalid_unfollow_user_data["result"]["message"]
            assert (response.status_code ==
                    invalid_unfollow_user_data["result"]["status_code"])
            assert response_data.keys() == expected_message.keys()
            assert response_data["result"] == expected_message["result"]
            assert isinstance(response_data["error_type"], str)
            assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=unfollow_user_method,
            url=user_can_unfollow_user["url"],
            headers=user_can_unfollow_user["header"],
        )
        assert response.json() == user_can_unfollow_user["result"]["message"]
        assert (response.status_code ==
                user_can_unfollow_user["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_user_can_not_unfollow_not_followed_user(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=unfollow_user_method,
            url=user_not_following_user["url"],
            headers=user_not_following_user["header"],
        )
        response_data = response.json()
        expected_message = user_not_following_user["result"]["message"]
        assert (response.status_code ==
                user_not_following_user["result"]["status_code"])
        assert response_data.keys() == expected_message.keys()
        assert response_data["result"] == expected_message["result"]
        assert isinstance(response_data["error_type"], str)
        assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_followed_details_removed_from_db(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        total_followed_before = await User.get_total_followed_by_name(
            user_can_unfollow_user["user_name"],
        )
        await client.request(
            method=unfollow_user_method,
            url=user_can_unfollow_user["url"],
            headers=user_can_unfollow_user["header"],
        )
        total_followed_after = await User.get_total_followed_by_name(
            user_can_unfollow_user["user_name"],
        )
        assert total_followed_before - 1 == total_followed_after
