"""Module for testing endpoint 'follow other user' from app.routes.py ."""
from httpx import AsyncClient
from pytest import mark as pytest_mark

from ..app.database import User
from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
    test_user_1,
)

follow_user_url = FAKE_TWITTER_ENDPOINTS["follow_user"]["endpoint"]
follow_user_method = FAKE_TWITTER_ENDPOINTS["follow_user"]["http_method"]
invalid_follow_user_data = {
    "urls": (
        follow_user_url.format(id="ten"),
        follow_user_url.format(id=()),
    ),
    "header": AUTHORIZED_HEADER,
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}
user_can_follow_user = {
    "user_id": test_user_1["id"],
    "user_name": test_user_1["name"],
    "url": follow_user_url.format(id=3),
    "header": {"api-key": test_user_1["name"]},
    "result": {
        "message":  {"result": True}, "status_code": CREATED_STATUS_CODE,
    },
}
user_cannot_follow_user = {
    "user_id": test_user_1["id"],  # User has already followed user with id=2
    "url": follow_user_url.format(id=2),
    "header": {"api-key": test_user_1["name"]},
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
    },
}


class TestFollowOtherUserEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_path_parameter(
        client: AsyncClient,
    ) -> None:
        for i_url in invalid_follow_user_data["urls"]:
            response = await client.request(
                method=follow_user_method,
                url=i_url,
                headers=invalid_follow_user_data["header"],
            )
            response_data = response.json()
            expected_message = invalid_follow_user_data["result"]["message"]
            assert (response.status_code ==
                    invalid_follow_user_data["result"]["status_code"])
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
            method=follow_user_method,
            url=user_can_follow_user["url"],
            headers=user_can_follow_user["header"],
        )
        assert response.json() == user_can_follow_user["result"]["message"]
        assert (response.status_code ==
                user_can_follow_user["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_user_can_not_follow_user_two_times(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        response = await client.request(
            method=follow_user_method,
            url=user_cannot_follow_user["url"],
            headers=user_cannot_follow_user["header"],
        )
        response_data = response.json()
        expected_message = user_cannot_follow_user["result"]["message"]
        assert (response.status_code ==
                user_cannot_follow_user["result"]["status_code"])
        assert response_data.keys() == expected_message.keys()
        assert response_data["result"] == expected_message["result"]
        assert isinstance(response_data["error_type"], str)
        assert isinstance(response_data["error_message"], str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_that_followed_details_inserted_in_db(
        client: AsyncClient, init_test_data_for_db: None,
    ) -> None:
        total_followed_before = await User.get_total_followed_by_name(
            user_can_follow_user["user_name"],
        )
        await client.request(
            method=follow_user_method,
            url=user_can_follow_user["url"],
            headers=user_can_follow_user["header"],
        )
        total_followed_after = await User.get_total_followed_by_name(
            user_can_follow_user["user_name"],
        )
        assert total_followed_before + 1 == total_followed_after
