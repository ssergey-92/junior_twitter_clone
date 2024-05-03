from httpx import AsyncClient
from pytest import mark as pytest_mark

from .common_data_for_tests import AUTHORIZED_HEADER, FAKE_TWITTER_ENDPOINTS

template_tweet_feed = {
    "id": 1,
    "content": "string",
    "attachments": ["string"],
    "author": {
        "id": 1,
        "name": "string",
    },
    "likes": [
        {
            "user_id": 1,
            "name": "string"
        }
    ]
}
CORRECT_GET_TWEET_FEED_RESPONSE = {
    "result": True, "tweets": [template_tweet_feed]}


class TestGetTweetFeedEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
            client: AsyncClient,
            init_test_data_for_db: None) -> None:
        response = await client.request(
            method=FAKE_TWITTER_ENDPOINTS["get_tweet_feed"]["http_method"],
            url=FAKE_TWITTER_ENDPOINTS["get_tweet_feed"]["endpoint"],
            headers=AUTHORIZED_HEADER
        )
        response_details = response.json()
        assert (response_details.keys() ==
                CORRECT_GET_TWEET_FEED_RESPONSE.keys())
        assert (response_details["result"] ==
                CORRECT_GET_TWEET_FEED_RESPONSE["result"])
        assert (type(response_details["tweets"]) is
                type(CORRECT_GET_TWEET_FEED_RESPONSE["tweets"]))
        for i_tweet in response_details["tweets"]:
            assert type(i_tweet) is type(template_tweet_feed)
            assert i_tweet.keys() == template_tweet_feed.keys()
            assert type(i_tweet["id"]) is type(template_tweet_feed["id"])
            assert (type(i_tweet["content"]) is
                    type(template_tweet_feed["content"]))
            assert (type(i_tweet["attachments"]) is
                    type(template_tweet_feed["attachments"]))
            for i_attachment in i_tweet["attachments"]:
                assert (type(i_attachment) is
                        type(template_tweet_feed["attachments"][0]))
            assert (type(i_tweet["author"]) is
                    type(template_tweet_feed["author"]))
            assert (i_tweet["author"].keys() ==
                    template_tweet_feed["author"].keys())
            assert (type(i_tweet["author"]["name"]) is
                    type(template_tweet_feed["author"]["name"]))
            assert (type(i_tweet["author"]["id"]) is
                    type(template_tweet_feed["author"]["id"]))
            assert (type(i_tweet["likes"]) is
                    type(template_tweet_feed["likes"]))
            for i_like in i_tweet["likes"]:
                assert i_like.keys() == template_tweet_feed["likes"][0].keys()
                assert (type(i_like["user_id"]) is
                        type(template_tweet_feed["likes"][0]["user_id"]))
                assert (type(i_like["name"]) is
                        type(template_tweet_feed["likes"][0]["name"]))
        assert response.status_code == 200
