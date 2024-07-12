"""Module for handling logic for tweet feed."""

from app.models.media_files import MediaFile
from app.models.tweets import Tweet
from app.models.users import User
from common import create_unregister_response


async def create_tweet_feed(tweets: list[Tweet]) -> list:
    """Create tweet feed.

    Args:
        tweets (list[Tweet]): list of tweets

    Returns:
        list : tweet feed

    """
    tweet_feed = []
    for i_tweet in tweets:
        attachments = []
        if i_tweet.tweet_media_ids:
            attachments = await MediaFile.get_media_files_names(
                i_tweet.tweet_media_ids,
            )
        likes = []
        for i_like in i_tweet.likes:
            like_details = {
                "user_id": i_like.user_details.id,
                "name": i_like.user_details.name,
            }
            likes.append(like_details)
        tweet_details = {
            "id": i_tweet.id,
            "content": i_tweet.tweet_data,
            "attachments": attachments,
            "author": {
                "id": i_tweet.author.id,
                "name": i_tweet.author.name,
            },
            "likes": likes,
        }
        tweet_feed.append(tweet_details)
    return tweet_feed


async def get_full_tweet_feed() -> tuple[dict, int]:
    """Handle logic of get tweet feed endpoint.

    Create list of tweets with details sorted descending by likes and
    return success response details

    Returns:
        tuple[dict, int]: response message and status code

    """
    tweets = await Tweet.get_all_tweets_sorted_by_likes()
    tweet_feed = []
    if tweets:
        tweet_feed = await create_tweet_feed(tweets)
    response_message = {"result": True, "tweets": tweet_feed}
    return response_message, 200


# async def get_user_tweet_feed(api_key: str) -> tuple[dict, int]:
#     """Handle logic of get tweet feed endpoint.
#
#     If user 'api_key' is existed then create for user list of tweets details
#     of followed users and sort them descending by likes. Then return success
#     response details. Else return response with error.
#
#     Args:
#       api_key (str): username
#
#     Returns:
#       tuple[dict, int]: response message and status code
#
#     """
#     user = await User.get_user_by_name(api_key)
#     if not user:
#         return create_unregister_response()
#     followed_users_name = []
#     tweet_feed = []
#     for i_followed in user.followed:
#         followed_users_name.append(i_followed.name)
#     if followed_users_name:
#         tweets = await Tweet.get_tweets_by_author_sorted_by_likes(
#             followed_users_name,
#         )
#         if tweets:
#             tweet_feed = await create_tweet_feed(
#                 tweets,
#             )
#     response_message = {"result": True, "tweets": tweet_feed}
#     return response_message, 200
