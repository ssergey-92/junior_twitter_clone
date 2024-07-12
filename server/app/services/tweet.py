"""Module for handling logic for tweets."""

from typing import Optional

from app.models.tweets import Tweet
from app.models.tweet_likes import TweetLike
from app.schemas import AddTweetIn
from common import create_bad_request_response, create_forbidden_response
from media_file import delete_media_files


async def add_tweet(
    api_key: str, new_tweet: AddTweetIn,
) -> tuple[dict, int]:
    """Handle logic of add tweet endpoint.

    Add new tweet in db and return success response details.

    Args:
        api_key (str): user name
        new_tweet (AddTweetIn): new tweet details

    Returns:
        tuple[dict, int]: response message and status code

    """
    new_tweet_details = dict(new_tweet)
    tweet_id = await Tweet.add_tweet(
        **new_tweet_details, author_name=api_key,
    )
    return {"tweet_id": tweet_id}, 201


async def delete_tweet(
    api_key: str, tweet_id: int,
) -> tuple[Optional[dict], int]:
    """Handle logic of delete tweet endpoint.

    Check if user tries to delete his own tweet. If so delete tweet and
    corresponding tweet files from db and from system. Then return success
    response details. Else return response with error.

    Args:
        api_key (str): username
        tweet_id (int): tweet id

    Returns:
        tuple[dict, int]: response message and status code

    """
    deleted_details = await Tweet.delete_tweet(api_key, tweet_id)
    if not deleted_details:
        return create_forbidden_response(
            "You can delete only yours tweet which is posted!",
        )
    media_files_ids = deleted_details[1]
    if media_files_ids:
        await delete_media_files(
            api_key, media_files_ids,
        )

    return None, 201


async def dislike_tweet_by_id(
    api_key: str, tweet_id: int,
) -> tuple[Optional[dict], int]:
    """Handle logic of dislike tweet endpoint.

    Check if user liked tweet and tweet is existed. If so remove tweet like
    details from db and return success response details. Else return
    response with error.

    Args:
        api_key (str): username
        tweet_id (int): tweet id

    Returns:
        tuple[dict, int]: response message and status code

    """
    tweet_like_id = await TweetLike.dislike_tweet(api_key, tweet_id)
    if not tweet_like_id:
        return create_bad_request_response(
            "You did not like the tweet!",
        )

    return None, 201


async def like_tweet_by_id(
    api_key: str, tweet_id: int,
) -> tuple[Optional[dict], int]:
    """Handle logic of like tweet endpoint.

    Check if user does not like tweet and tweet is existed. If so return
    success response details. Else return response with error.

    Args:
        api_key (str): username
        tweet_id (int): tweet id

    Returns:
        tuple[dict, int]: response message and status code

    """
    tweet_like_id = await TweetLike.like_tweet(api_key, tweet_id)
    if not tweet_like_id:
        return create_bad_request_response(
            "You have already liked the tweet!",
        )

    return None, 201
