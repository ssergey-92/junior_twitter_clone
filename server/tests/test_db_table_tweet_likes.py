"""Module for testing methods of class TweetLike from app.database.py ."""
from pytest import mark as pytest_mark

from ..app.database import TweetLike
from .common_data_for_tests import (
    DEFAULT_TOTAL_LIKES,
    test_user_1,
    test_user_2,
    test_user_3,
)

user_did_not_like_tweet = [
    {"tweet_id": 1, "user_name": test_user_2["name"]},
    {"tweet_id": 1, "user_name": test_user_3["name"]},
    {"tweet_id": 2, "user_name": test_user_1["name"]},
]
user_has_liked_tweet = [
    {"tweet_id": 1, "user_name": test_user_1["name"]},
    {"tweet_id": 2, "user_name": test_user_3["name"]},
    {"tweet_id": 3, "user_name": test_user_2["name"]},
]


class TestTweetLikeMethods:
    @staticmethod
    @pytest_mark.asyncio
    async def test_like_tweet(init_test_data_for_db: None) -> None:
        for i_like_details in user_did_not_like_tweet:
            like_id = await TweetLike.like_tweet(**i_like_details)
            assert isinstance(like_id, int)
        for i_like_details in user_has_liked_tweet:
            like_id = await TweetLike.like_tweet(**i_like_details)
            assert like_id is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_dislike_tweet(init_test_data_for_db: None) -> None:
        for i_like_details in user_did_not_like_tweet:
            like_id = await TweetLike.dislike_tweet(**i_like_details)
            assert like_id is None
        for i_like_details in user_has_liked_tweet:
            like_id = await TweetLike.dislike_tweet(**i_like_details)
            assert isinstance(like_id, int)

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_total_likes(init_test_data_for_db: None) -> None:
        total_likes = await TweetLike.get_total_likes()
        assert total_likes == DEFAULT_TOTAL_LIKES
