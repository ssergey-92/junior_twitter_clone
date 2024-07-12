"""Module for testing logic for tweet feed from services/tweet_feed.py ."""

from pytest import mark as pytest_mark

from app.models.tweets import Tweet

from ..app.services import tweet_feed
from .common import (
    CORRECT_GET_TWEET_FEED_RESPONSE,
    CORRECT_GET_TWEET_FEED_RESPONSE_2,
    SORTED_TWEET_FEED,
)


class TestServicesTweetFeed:
    @staticmethod
    @pytest_mark.asyncio
    async def test_create_tweet_feed(init_test_data_for_db: None) -> None:
        all_sorted_tweets = await Tweet.get_all_tweets_sorted_by_likes()
        tweet_feed_data = await tweet_feed.create_tweet_feed(all_sorted_tweets)
        assert tweet_feed_data == SORTED_TWEET_FEED

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_full_tweet_feed(init_test_data_for_db: None) -> None:
        tweet_feed_data, status_code = await tweet_feed.get_full_tweet_feed()
        assert tweet_feed_data == CORRECT_GET_TWEET_FEED_RESPONSE["tweet_feed"]
        assert status_code == CORRECT_GET_TWEET_FEED_RESPONSE["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_full_tweet_feed_from_empty_tables(
            clear_test_db_tables: None,
    ) -> None:
        tweet_feed_data, status_code = await tweet_feed.get_full_tweet_feed()
        assert (tweet_feed_data ==
                CORRECT_GET_TWEET_FEED_RESPONSE_2["tweet_feed"])
        assert status_code == CORRECT_GET_TWEET_FEED_RESPONSE_2["status_code"]
