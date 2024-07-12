"""Module for testing class Tweet from app.models.tweets.py ."""

from pytest import mark as pytest_mark

from app.models.tweets import Tweet
from .common import (
    DEFAULT_TOTAL_TWEETS,
    TWEET_1,
    TWEET_2,
    TWEET_3,
    test_user_1,
)

new_tweet = {
    "author_name": test_user_1["name"],
    "tweet_data": "new tweet for teat user_1",
    "tweet_media_ids": [4, 5],
}


class TestTableTweetMethods:

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_tweet(init_test_data_for_db: None) -> None:
        tweet_id = await Tweet.add_tweet(**new_tweet)
        assert tweet_id == DEFAULT_TOTAL_TWEETS + 1

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_tweet(init_test_data_for_db: None) -> None:
        deleted_details = await Tweet.delete_tweet(
            author_name=TWEET_1["author_name"], tweet_id=TWEET_1["id"],
        )
        assert deleted_details == (
            TWEET_1["tweet_data"],
            TWEET_1["tweet_media_ids"],
        )

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_total_tweets(init_test_data_for_db: None) -> None:
        total_tweets = await Tweet.get_total_tweets()
        assert total_tweets == DEFAULT_TOTAL_TWEETS

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_all_tweets_sorted_by_likes(
        init_test_data_for_db: None,
    ) -> None:
        all_tweets = await Tweet.get_all_tweets_sorted_by_likes()
        assert len(all_tweets) == DEFAULT_TOTAL_TWEETS
        for i_tweet in all_tweets:
            assert isinstance(i_tweet, Tweet)
        assert all_tweets[0].id == TWEET_3["id"]
        assert all_tweets[1].id == TWEET_2["id"]
        assert all_tweets[2].id == TWEET_1["id"]
