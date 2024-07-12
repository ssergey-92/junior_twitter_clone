"""Module for testing logic for user from services/user.py ."""

from pytest import mark as pytest_mark

from ..app.services import user
from .common import (
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    test_user_1,
)

unregister_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
bad_request_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
user_can_follow_user = {
    "api_key": test_user_1["name"],
    "followed_id": 3,
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
unexist_user = {
    "id": 0,
    "name": "unexsit_user",
}
user_cannot_follow_user = (
    {
        "api_key": test_user_1["name"],  # user has already followed him
        "followed_id": test_user_1["followed"][0]["id"],
        "result": bad_request_response,
    },
    {
        "api_key": unexist_user["name"],
        "followed_id": test_user_1["followed"][0]["id"],
        "result": unregister_response,
    },
    {
        "api_key": test_user_1["name"],
        "followed_id": 0,  # followed user is not existed
        "result": unregister_response,
    },
)
user_can_unfollow_user = {
    "api_key": test_user_1["name"],
    "followed_id": test_user_1["followed"][0]["id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
user_cannot_unfollow_user = (
    {
        "api_key": test_user_1["name"],  # user does not follow him
        "followed_id": 3,
        "result": bad_request_response,
    },
    {
        "api_key": unexist_user["name"],
        "followed_id": test_user_1["followed"][0]["id"],
        "result": unregister_response,
    },
    {
        "api_key": test_user_1["name"],
        "followed_id": 0,  # followed user is not existed
        "result": unregister_response,
    },
)


class TestServiceUser:
    @staticmethod
    @pytest_mark.asyncio
    async def test_follow_other_user(init_test_data_for_db: None) -> None:
        message, status_code = await user.follow_other_user(
            user_can_follow_user["api_key"],
            user_can_follow_user["followed_id"],
        )
        assert message == user_can_follow_user["result"]["message"]
        assert status_code == user_can_follow_user["result"]["status_code"]
        for i_data in user_cannot_follow_user:
            message, status_code = await user.follow_other_user(
                i_data["api_key"], i_data["followed_id"],
            )
            assert message.keys() == i_data["result"]["message"].keys()
            assert message["result"] == i_data["result"]["message"]["result"]
            assert status_code == i_data["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_unfollow_other_user(init_test_data_for_db: None) -> None:
        message, status_code = await user.unfollow_user(
            user_can_unfollow_user["api_key"],
            user_can_unfollow_user["followed_id"],
        )
        assert message == user_can_unfollow_user["result"]["message"]
        assert status_code == user_can_unfollow_user["result"]["status_code"]
        for i_data in user_cannot_unfollow_user:
            message, status_code = await user.unfollow_user(
                i_data["api_key"], i_data["followed_id"],
            )
            assert message.keys() == i_data["result"]["message"].keys()
            assert message["result"] == i_data["result"]["message"]["result"]
            assert status_code == i_data["result"]["status_code"]
