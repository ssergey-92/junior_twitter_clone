"""Module for testing logic for tweet from services/tweet.py ."""

from pytest import mark as pytest_mark


from ..app.services import tweet
from .common import (
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    FORBIDDEN_STATUS_CODE,
    LIKE_1_1,
    TWEET_1,
    TWEET_2,
    test_user_1,
    test_user_2,
)

new_tweets_to_add = (
    {
        "new_tweet": {"tweet_data": "tweet # 4"},
        "api_key": test_user_1["name"],
        "result": {
            "message": {"tweet_id": 4}, "status_code": CREATED_STATUS_CODE,
        },
    },
    {
        "new_tweet": {"tweet_data": "tweet # 5"},
        "api_key": test_user_1["name"],
        "result": {
            "message": {"tweet_id": 5}, "status_code": CREATED_STATUS_CODE,
        },
    },
)
bad_request_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
forbidden_response = {
            "message": ERROR_MESSAGE, "status_code": FORBIDDEN_STATUS_CODE,
        }
valid_delete_tweet_data = {
    "api_key": test_user_1["name"],
    "tweet_id": TWEET_1["id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
invalid_delete_tweet_data = {
    "api_key": test_user_1["name"],  # belongs to test_user_1
    "tweet_id": TWEET_2["id"],
    "result": forbidden_response,
}
valid_data_dislike_tweet = {
    "api_key": LIKE_1_1["user_name"],
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
invalid_data_dislike_tweet = {
    "api_key": test_user_2["name"],  # Only test_user_1 liked tweet
    "tweet_id": TWEET_1["id"],
    "result": bad_request_response,
}
valid_data_like_tweet = {
    "api_key": test_user_2["name"],
    "tweet_id": TWEET_1["id"],
    "result": {"message": None, "status_code": CREATED_STATUS_CODE},
}
invalid_data_like_tweet = {
    "api_key": LIKE_1_1["user_name"],  # user has already liked tweet
    "tweet_id": LIKE_1_1["tweet_id"],
    "result": bad_request_response,
}


class TestServicesTweet:

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_tweet(
        add_paths_to_os_environ: None, init_test_data_for_db: None,
    ) -> None:
        for i_data in new_tweets_to_add:
            message, status_code = await tweet.add_tweet(
                i_data["api_key"], i_data["new_tweet"],
            )
            assert message == i_data["result"]["message"]
            assert status_code == i_data["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_tweet(
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        message, status_code = await tweet.delete_tweet(
            valid_delete_tweet_data["api_key"],
            valid_delete_tweet_data["tweet_id"],
        )
        assert message == valid_delete_tweet_data["result"]["message"]
        assert status_code == valid_delete_tweet_data["result"]["status_code"]
        message, status_code = await tweet.delete_tweet(
            invalid_delete_tweet_data["api_key"],
            invalid_delete_tweet_data["tweet_id"],
        )
        assert (message.keys() ==
                invalid_delete_tweet_data["result"]["message"].keys())
        assert (message["result"] ==
                invalid_delete_tweet_data["result"]["message"]["result"])
        assert (status_code ==
                invalid_delete_tweet_data["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_dislike_tweet_by_id(init_test_data_for_db: None) -> None:
        message, status_code = await tweet.dislike_tweet_by_id(
            valid_data_dislike_tweet["api_key"],
            valid_data_dislike_tweet["tweet_id"],
        )
        assert message == valid_data_dislike_tweet["result"]["message"]
        assert status_code == valid_data_dislike_tweet["result"]["status_code"]
        message, status_code = await tweet.dislike_tweet_by_id(
            invalid_data_dislike_tweet["api_key"],
            invalid_data_dislike_tweet["tweet_id"],
        )
        assert (message.keys() ==
                invalid_data_dislike_tweet["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_dislike_tweet["result"]["message"]["result"])
        assert (status_code ==
                invalid_data_dislike_tweet["result"]["status_code"])

    @staticmethod
    @pytest_mark.asyncio
    async def test_like_tweet_by_id(init_test_data_for_db: None) -> None:
        message, status_code = await tweet.like_tweet_by_id(
            valid_data_like_tweet["api_key"],
            valid_data_like_tweet["tweet_id"],
        )
        assert message == valid_data_like_tweet["result"]["message"]
        assert status_code == valid_data_like_tweet["result"]["status_code"]
        message, status_code = await tweet.like_tweet_by_id(
            invalid_data_like_tweet["api_key"],
            invalid_data_like_tweet["tweet_id"],
        )
        assert (message.keys() ==
                invalid_data_like_tweet["result"]["message"].keys())
        assert (message["result"] ==
                invalid_data_like_tweet["result"]["message"]["result"])
        assert status_code == invalid_data_like_tweet["result"]["status_code"]
