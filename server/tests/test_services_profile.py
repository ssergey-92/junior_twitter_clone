"""Module for testing logic for profile from services/profile.py ."""

from pytest import mark as pytest_mark

from app.models.users import User
from ..app.services import profile
from .common import (
    BAD_REQUEST_STATUS_CODE,
    CORRECT_GET_OWN_PROFILE_RESPONSE,
    CORRECT_GET_USER_PROFILE_RESPONSE,
    ERROR_MESSAGE,
    FORBIDDEN_STATUS_CODE,
    test_user_profile,
)

unregister_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
bad_request_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
forbidden_response = {
            "message": ERROR_MESSAGE, "status_code": FORBIDDEN_STATUS_CODE,
        }
unexist_user = {
    "id": 0,
    "name": "unexsit_user",
}
invalid_data_get_user_profile = {
    "result": unregister_response, "id": unexist_user["id"],
}
invalid_data_get_own_profile = {
    "result": unregister_response, "api_key": unexist_user["name"],
}


class TestServicesUser:

    @staticmethod
    @pytest_mark.asyncio
    async def test_create_user_profile(init_test_data_for_db: None) -> None:
        user = await User.get_user_by_id(test_user_profile["id"])
        assert profile.create_user_profile(user) == test_user_profile


    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_profile(init_test_data_for_db: None) -> None:
        user_profile, status_code = await profile.get_user_profile(
            CORRECT_GET_USER_PROFILE_RESPONSE["profile"]["user"]["id"],
        )
        assert (user_profile ==
                CORRECT_GET_USER_PROFILE_RESPONSE["profile"])
        assert (status_code ==
                CORRECT_GET_USER_PROFILE_RESPONSE["status_code"])
        message, status_code = await profile.get_user_profile(
            invalid_data_get_user_profile["id"],
        )
        assert (message.keys() ==
                invalid_data_get_user_profile["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_get_user_profile["result"]["message"]["result"])
        assert (status_code ==
                invalid_data_get_user_profile["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_own_profile(init_test_data_for_db: None) -> None:
        own_profile, status_code = await profile.get_own_profile(
            CORRECT_GET_OWN_PROFILE_RESPONSE["profile"]["user"]["name"],
        )
        assert own_profile == CORRECT_GET_OWN_PROFILE_RESPONSE["profile"]
        assert status_code == CORRECT_GET_OWN_PROFILE_RESPONSE["status_code"]
        message, status_code = await profile.get_own_profile(
            invalid_data_get_own_profile["api_key"],
        )
        assert (message.keys() ==
                invalid_data_get_own_profile["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_get_own_profile["result"]["message"]["result"])
        assert (status_code ==
                invalid_data_get_own_profile["result"]["status_code"])
