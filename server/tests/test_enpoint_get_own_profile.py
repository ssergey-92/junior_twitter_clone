from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import AUTHORIZED_HEADER, FAKE_TWITTER_ENDPOINTS

own_profile = {
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
CORRECT_GET_OWN_PROFILE_RESPONSE = {
    "result": True, "user": own_profile}


class TestGetOwnProfileEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        response = await client.request(
            method=FAKE_TWITTER_ENDPOINTS["get_own_profile"]["http_method"],
            url=FAKE_TWITTER_ENDPOINTS["get_own_profile"]["endpoint"],
            headers=AUTHORIZED_HEADER
        )
        response_details = response.json()
        assert (response_details.keys() ==
                CORRECT_GET_OWN_PROFILE_RESPONSE.keys())
        assert (response_details["result"] ==
                CORRECT_GET_OWN_PROFILE_RESPONSE["result"])
        assert (type(response_details["user"]) is
                type(CORRECT_GET_OWN_PROFILE_RESPONSE["user"]))
        assert response_details["user"].keys() == own_profile.keys()
        assert (type(response_details["user"]["id"]) is
                type(own_profile["id"]))
        assert (type(response_details["user"]["name"]) is
                type(own_profile["name"]))
        assert (type(response_details["user"]["followers"]) is
                type(own_profile["followers"]))
        assert (type(response_details["user"]["following"]) is
                type(own_profile["following"]))
        for i_follower in response_details["user"]["followers"]:
            assert type(i_follower) is type(own_profile["followers"][0])
            assert i_follower.keys() == own_profile["followers"][0].keys()
            assert (type(i_follower["id"]) is
                    type(own_profile["followers"][0]["id"]))
            assert (type(i_follower["name"]) is
                    type(own_profile["followers"][0]["name"]))
        for i_following in response_details["user"]["following"]:
            assert type(i_following) is type(own_profile["following"][0])
            assert i_following.keys() == own_profile["following"][0].keys()
            assert (type(i_following["id"]) is
                    type(own_profile["following"][0]["id"]))
            assert (type(i_following["name"]) is
                    type(own_profile["following"][0]["name"]))
        assert response.status_code == 200
