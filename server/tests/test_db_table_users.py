from pytest import mark as pytest_mark

from ..app.database import User
from .common_data_for_tests import test_user_1, test_user_2, test_user_3


EXIST_USERS = [test_user_1, test_user_2, test_user_3]
UNEXIST_USERS = [
    {"name": "unexist_11", "id": 11},
    {"name": "unexist_22", "id": 22},
    {"name": "unexist_33", "id": 33}
]
NEW_USER = {"name": "new_user", "id": 4, "followers": [], "followed": []}
USER_CAN_FOLLOW_USER = [
    {"user": test_user_1["id"], "followed": test_user_3["id"]},
    {"user": test_user_2["id"], "followed": test_user_1["id"]},
    {"user": test_user_2["id"], "followed": test_user_3["id"]},
    {"user": test_user_3["id"], "followed": test_user_2["id"]}
]
USER_CAN_NOT_FOLLOW_USER = [
    {"user": test_user_1["id"], "followed": test_user_2["id"]},
    {"user": test_user_3["id"], "followed": test_user_1["id"]}
]
USER_CAN_UNFOLLOW_USER = [
    {"user": test_user_1["id"], "followed": test_user_2["id"]},
    {"user": test_user_3["id"], "followed": test_user_1["id"]}
]
USER_CAN_NOT_UNFOLLOW_USER = [
    {"user": test_user_1["id"], "followed": test_user_3["id"]},
    {"user": test_user_2["id"], "followed": test_user_1["id"]},
    {"user": test_user_2["id"], "followed": test_user_3["id"]},
    {"user": test_user_3["id"], "followed": test_user_2["id"]}
]
class TestTableUserMethods:

    @staticmethod
    @pytest_mark.asyncio
    async def test_is_existed_user_name(init_test_data_for_db: None) -> None:
        for i_exist_user in EXIST_USERS:
            assert (await User.is_existed_user_name(i_exist_user["name"]) is
                    True)
        for i_unexist_user in UNEXIST_USERS:
            assert (await User.is_existed_user_name(i_unexist_user["name"]) is
                    False)

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_id_by_name(init_test_data_for_db: None) -> None:
        for i_exist_user in EXIST_USERS:
            assert (await User.get_user_id_by_name(i_exist_user["name"]) ==
                    i_exist_user["id"])
        for i_unexist_user in UNEXIST_USERS:
            assert (await User.get_user_id_by_name(i_unexist_user["name"]) is
                    None)

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_by_name(init_test_data_for_db: None) -> None:
        for i_exist_user in EXIST_USERS:
            user = await User.get_user_by_name(i_exist_user["name"])
            assert user.name == i_exist_user["name"]
            assert user.id == i_exist_user["id"]
            for index, i_follower in enumerate(user.followers):
                assert (i_follower.name ==
                        i_exist_user["followers"][index]["name"])
                assert i_follower.id == i_exist_user["followers"][index]["id"]
            for index, i_followed in enumerate(user.followed):
                assert (i_followed.name ==
                        i_exist_user["followed"][index]["name"])
                assert i_followed.id == i_exist_user["followed"][index]["id"]
        for i_unexist_name in UNEXIST_USERS:
            assert (await User.get_user_by_name(i_unexist_name["name"]) is
                    None)

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_by_id(init_test_data_for_db: None) -> None:
        for i_exist_user in EXIST_USERS:
            user = await User.get_user_by_id(i_exist_user["id"])
            assert user.name == i_exist_user["name"]
            assert user.id == i_exist_user["id"]
            for index, i_follower in enumerate(user.followers):
                assert (i_follower.name ==
                        i_exist_user["followers"][index]["name"])
                assert i_follower.id == i_exist_user["followers"][index]["id"]
            for index, i_followed in enumerate(user.followed):
                assert (i_followed.name ==
                        i_exist_user["followed"][index]["name"])
                assert i_followed.id == i_exist_user["followed"][index]["id"]
        for i_unexist_user in UNEXIST_USERS:
            assert await User.get_user_by_id(i_unexist_user["id"]) is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_user(recreate_all_tables: None) -> None:
        await User.add_user(NEW_USER["name"])
        assert (await User.is_existed_user_name(NEW_USER["name"]) is
                True)

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_total_followed_by_name(
            init_test_data_for_db: None) -> None:
        for i_exist_user in EXIST_USERS:
            total_followed = await User.get_total_followed_by_name(
                i_exist_user["name"]
            )
            assert total_followed == len(i_exist_user["followed"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_follow_other_user(
            init_test_data_for_db: None) -> None:
        for i_followed_details in USER_CAN_FOLLOW_USER:
            result = await User.follow_other_user(
                i_followed_details["user"], i_followed_details["followed"]
            )
            assert result is not None
        for i_followed_details in USER_CAN_NOT_FOLLOW_USER:
            result = await User.follow_other_user(
                i_followed_details["user"], i_followed_details["followed"]
            )
            assert result is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_unfollow_user(
            init_test_data_for_db: None) -> None:
        for i_followed_details in USER_CAN_UNFOLLOW_USER:
            result = await User.unfollow_user(
                i_followed_details["user"], i_followed_details["followed"]
            )
            assert result is not None
        for i_followed_details in USER_CAN_NOT_UNFOLLOW_USER:
            result = await User.unfollow_user(
                i_followed_details["user"], i_followed_details["followed"]
            )
            assert result is None
