from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS
)

get_user_profile_endpoint = (
    FAKE_TWITTER_ENDPOINTS["get_user_profile"]["endpoint"]
)
GET_USER_PROFILE_HTTP_METHOD = (
    FAKE_TWITTER_ENDPOINTS["get_user_profile"]["http_method"]
)
exist_user_id = 2
unexist_user_id = 0
user_profile = {
    "id": 1,
    "name": "string",
    "followers": [
        {
            "id": 1,
            "name": "string",
        }
    ],
    "following": [
        {
            "id": 1,
            "name": "string",
        }
    ]
}
CORRECT_USER_PROFILE_RESPONSE = {
    "result": True, "user": user_profile}


class TestGetUserProfileEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_if_user_not_existed(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        response = await client.request(
            method=GET_USER_PROFILE_HTTP_METHOD,
            url=get_user_profile_endpoint.format(id=unexist_user_id),
            headers=AUTHORIZED_HEADER
        )
        response_data = response.json()
        assert response.status_code == BAD_REQUEST_STATUS_CODE
        assert response_data.get("result", None) == \
               ERROR_MESSAGE["result"]
        assert response_data.keys() == ERROR_MESSAGE.keys()
        assert isinstance(response_data.get("error_type", None), str)
        assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        response = await client.request(
            method=GET_USER_PROFILE_HTTP_METHOD,
            url=get_user_profile_endpoint.format(id=exist_user_id),
            headers=AUTHORIZED_HEADER
        )
        response_details = response.json()
        assert (response_details.keys() ==
                CORRECT_USER_PROFILE_RESPONSE.keys())
        assert (response_details["result"] ==
                CORRECT_USER_PROFILE_RESPONSE["result"])
        assert (type(response_details["user"]) is
                type(CORRECT_USER_PROFILE_RESPONSE["user"]))
        assert response_details["user"].keys() == user_profile.keys()
        assert (type(response_details["user"]["id"]) is
                type(user_profile["id"]))
        assert (type(response_details["user"]["name"]) is
                type(user_profile["name"]))
        assert (type(response_details["user"]["followers"]) is
                type(user_profile["followers"]))
        assert (type(response_details["user"]["following"]) is
                type(user_profile["following"]))
        for i_follower in response_details["user"]["followers"]:
            assert type(i_follower) is type(user_profile["followers"][0])
            assert i_follower.keys() == user_profile["followers"][0].keys()
            assert (type(i_follower["id"]) is
                    type(user_profile["followers"][0]["id"]))
            assert (type(i_follower["name"]) is
                    type(user_profile["followers"][0]["name"]))
        for i_following in response_details["user"]["following"]:
            assert type(i_following) is type(user_profile["following"][0])
            assert i_following.keys() == user_profile["following"][0].keys()
            assert (type(i_following["id"]) is
                    type(user_profile["following"][0]["id"]))
            assert (type(i_following["name"]) is
                    type(user_profile["following"][0]["name"]))
        assert response.status_code == 200
