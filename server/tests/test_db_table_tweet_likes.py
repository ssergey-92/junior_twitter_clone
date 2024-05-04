from httpx import AsyncClient
from pytest import mark as pytest_mark

from ..app.database import TweetLike
from .common_data_for_tests import (
    DEFAULT_TOTAL_LIKES,
    test_user_1,
    test_user_2,
    test_user_3
)

USER_DID_NOT_LIKE_TWEET = [
    {"tweet_id": 1, "user_name": test_user_2["name"]},
    {"tweet_id": 1, "user_name": test_user_3["name"]},
    {"tweet_id": 2, "user_name": test_user_1["name"]}
]
USER_HAS_LIKED_TWEET = [
    {"tweet_id": 1, "user_name": test_user_1["name"]},
    {"tweet_id": 2, "user_name": test_user_3["name"]},
    {"tweet_id": 3, "user_name": test_user_2["name"]}
]


class TestTweetLikeMethods:
    @staticmethod
    @pytest_mark.asyncio
    async def test_like_tweet(init_test_data_for_db: None) -> None:
        for i_like_details in USER_DID_NOT_LIKE_TWEET:
            like_id = await TweetLike.like_tweet(**i_like_details)
            assert like_id is not None
        for i_like_details in USER_HAS_LIKED_TWEET:
            like_id = await TweetLike.like_tweet(**i_like_details)
            assert like_id is None

    @staticmethod
    @pytest_mark.asyncio
    async def test_dislike_tweet(init_test_data_for_db: None) -> None:
        for i_like_details in USER_DID_NOT_LIKE_TWEET:
            like_id = await TweetLike.dislike_tweet(**i_like_details)
            assert like_id is None
        for i_like_details in USER_HAS_LIKED_TWEET:
            like_id = await TweetLike.dislike_tweet(**i_like_details)
            assert like_id is not None

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_total_likes(init_test_data_for_db: None) -> None:
        total_likes = await TweetLike.get_total_likes()
        assert total_likes == DEFAULT_TOTAL_LIKES

