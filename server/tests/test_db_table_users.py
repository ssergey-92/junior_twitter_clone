"""Module for testing methods of class User from app.database.py ."""
from pytest import mark as pytest_mark

from ..app.database import User
from .common_data_for_tests import test_user_1, test_user_2, test_user_3

exist_users = (test_user_1, test_user_2, test_user_3)
unexist_users = (
    {"name": "unexist_11", "id": 11},
    {"name": "unexist_22", "id": 22},
    {"name": "unexist_33", "id": 33},
)
users_for_exist_check = (
    {
        "users": exist_users,
        "result": True,
    },
    {
        "users": unexist_users,
        "result": False,
    },
)
new_user = {"name": "new_user", "id": 4, "followers": [], "followed": []}
user_can_follow_user = (
    {
        "user": test_user_1["id"],
        "followed": test_user_3["id"],
        "result": (test_user_1["id"], test_user_3["id"]),
    },
    {
        "user": test_user_2["id"],
        "followed": test_user_1["id"],
        "result": (test_user_2["id"], test_user_1["id"]),
    },
    {
        "user": test_user_2["id"],
        "followed": test_user_3["id"],
        "result": (test_user_2["id"], test_user_3["id"]),
    },
    {
        "user": test_user_3["id"],
        "followed": test_user_2["id"],
        "result": (test_user_3["id"], test_user_2["id"]),
    },
)
user_can_not_follow_user = (
    {"user": test_user_1["id"], "followed": test_user_2["id"], "result": None},
    {"user": test_user_3["id"], "followed": test_user_1["id"], "result": None},
)
user_follow_data = (*user_can_follow_user, *user_can_not_follow_user)
user_can_unfollow_user = (
    {
        "user": test_user_1["id"],
        "followed": test_user_2["id"],
        "result": (test_user_1["id"], test_user_2["id"]),
    },
    {
        "user": test_user_3["id"],
        "followed": test_user_1["id"],
        "result": (test_user_3["id"], test_user_1["id"]),
    },
)
user_can_not_unfollow_user = (
    {"user": test_user_1["id"], "followed": test_user_3["id"], "result": None},
    {"user": test_user_2["id"], "followed": test_user_1["id"], "result": None},
    {"user": test_user_2["id"], "followed": test_user_3["id"], "result": None},
    {"user": test_user_3["id"], "followed": test_user_2["id"], "result": None},
)
user_unfollow_data = (*user_can_unfollow_user, *user_can_not_unfollow_user)


class TestTableUserMethods:

    @staticmethod
    @pytest_mark.asyncio
    async def test_is_existed_user_name(init_test_data_for_db: None) -> None:
        for users in users_for_exist_check:
            for i_user in users["users"]:
                is_exist = await User.is_existed_user_name(i_user["name"])
                assert is_exist == users["result"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_id_by_name(init_test_data_for_db: None) -> None:
        for exist_i_user in exist_users:
            user_id = await User.get_user_id_by_name(exist_i_user["name"])
            assert user_id == exist_i_user["id"]
        for unexist_i_user in unexist_users:
            user_id = await User.get_user_id_by_name(unexist_i_user["name"])
            assert user_id is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_by_name(init_test_data_for_db: None) -> None:
        for i_exist_user in exist_users:
            user = await User.get_user_by_name(i_exist_user["name"])
            assert user.name == i_exist_user["name"]
            assert user.id == i_exist_user["id"]
            for index, i_follower in enumerate(user.followers):
                assert (
                    i_follower.name == i_exist_user["followers"][index]["name"]
                )
                assert i_follower.id == i_exist_user["followers"][index]["id"]
            for index, i_followed in enumerate(user.followed):
                assert (
                    i_followed.name == i_exist_user["followed"][index]["name"]
                )
                assert i_followed.id == i_exist_user["followed"][index]["id"]
        for i_unexist_name in unexist_users:
            assert await User.get_user_by_name(i_unexist_name["name"]) is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_user_by_id(init_test_data_for_db: None) -> None:
        for i_exist_user in exist_users:
            user = await User.get_user_by_id(i_exist_user["id"])
            assert user.name == i_exist_user["name"]
            assert user.id == i_exist_user["id"]
            for index, i_follower in enumerate(user.followers):
                assert (
                    i_follower.name == i_exist_user["followers"][index]["name"]
                )
                assert i_follower.id == i_exist_user["followers"][index]["id"]
            for index, i_followed in enumerate(user.followed):
                assert (
                    i_followed.name == i_exist_user["followed"][index]["name"]
                )
                assert i_followed.id == i_exist_user["followed"][index]["id"]
        for i_unexist_user in unexist_users:
            assert await User.get_user_by_id(i_unexist_user["id"]) is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_user(recreate_all_tables: None) -> None:
        await User.add_user(new_user["name"])
        assert await User.is_existed_user_name(new_user["name"]) is True

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_total_followed_by_name(
        init_test_data_for_db: None,
    ) -> None:
        for i_exist_user in exist_users:
            total_followed = await User.get_total_followed_by_name(
                i_exist_user["name"],
            )
            assert total_followed == len(i_exist_user["followed"])
        for i_unexist_user in unexist_users:
            total_followed = await User.get_total_followed_by_name(
                i_unexist_user["name"],
            )
            assert total_followed is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_follow_other_user(init_test_data_for_db: None) -> None:
        for i_data in user_follow_data:
            result = await User.follow_other_user(
                i_data["user"], i_data["followed"],
            )
            assert result == i_data["result"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_unfollow_user(init_test_data_for_db: None) -> None:
        for i_data in user_unfollow_data:
            result = await User.unfollow_user(
                i_data["user"], i_data["followed"],
            )
            assert result == i_data["result"]
