from asyncio import to_thread as asyncio_to_thread
from os import path as os_path
from typing import Optional, Sequence

from aiofiles import open as aio_open
from fastapi import UploadFile

from database import User, MediaFile, Tweet, TweetLike
from schemas import AddTweetIn

IMAGES_PATH = '/usr/share/nginx/html/images'
user_template_details = {
    "id": 0,
    "name": "",
    "followers": [],
    "following": [],
}

error_message = {
    "result": False,
    "error_type": "",
    "error_message": "",
}


class HandleEndpoint:

    @staticmethod
    def _create_user_profile(user: User) -> dict:
        user_profile = {
            "id": user.id,
            "name": user.name,
            "followers": [],
            "following": [],
        }
        for i_follower in user.followers:
            user_profile["followers"].append(
                {
                    "id": i_follower.id,
                    "name": i_follower.name,
                }
            )
        for i_followed in user.followed:
            user_profile["following"].append(
                {
                    "id": i_followed.id,
                    "name": i_followed.name,
                }
            )

        return user_profile

    @staticmethod
    async def _create_tweet_feed(tweets: Sequence[Tweet]) -> list:
        tweet_feed = list()
        for i_tweet in tweets:
            if not i_tweet.tweet_media_ids:
                attachments = list()
            else:
                attachments = await MediaFile.get_media_files_names(
                    i_tweet.tweet_media_ids
                )
            tweet_details = {
                'id': i_tweet.id,
                'content': i_tweet.tweet_data,
                'attachments': attachments,
                'author': {
                    'id': i_tweet.author.id,
                    'name': i_tweet.author.name,
                },
                'likes': list()
            }
            for i_like in i_tweet.likes:
                like_details = {
                    'user_id': i_like.user_details.id,
                    'name': i_like.user_details.name,
                }
                tweet_details['likes'].append(like_details)
            tweet_feed.append(tweet_details)

        return tweet_feed

    @staticmethod
    async def _permission_check(api_key: str) -> Optional[tuple[dict, int]]:
        if not await User.is_existed_user_name(api_key):
            error_message["error_type"] = "Unauthorized"
            error_message["error_message"] = (
                "You don't have permission for operation!"
            )
            return error_message, 400
        else:
            return None

    @staticmethod
    async def _follow_unfollow_check(api_key: str, followed_id: int) \
            -> Optional[tuple[dict, int]]:
        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            if await User.is_existed_user_id(followed_id):
                return None
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    f"Followed user with id: {followed_id} is not existed"
                )
            return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def _like_dislike_tweet_check(api_key: str, tweet_id: int) \
            -> Optional[tuple[dict, int]]:
        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            tweet_existed = await Tweet.is_existed(tweet_id)
            if tweet_existed:
                return None
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    f"Tweet with id: {tweet_id} is not existed"
                )
            return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def _save_media_file(media_file: UploadFile) -> None:
        media_file_path = os_path.join(IMAGES_PATH, media_file.filename)
        async with aio_open(media_file_path, 'wb') as out_file:
            media_file_data = await media_file.read()
            await out_file.write(media_file_data)

    @staticmethod
    async def add_tweet(api_key: str, new_tweet: AddTweetIn) \
            -> tuple[dict, int]:

        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            new_tweet_details = dict(new_tweet)
            tweet_id = await Tweet.add_tweet(
                **new_tweet_details,
                author_name=api_key
            )
            return {"tweet_id": tweet_id}, 201
        else:
            return restrictions_details

    @staticmethod
    async def add_media_file(api_key: str, file: UploadFile) -> tuple[dict, int]:
        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            await HandleEndpoint._save_media_file(file)
            filename = './{name}'.format(name=file.filename)
            media_id = await MediaFile.add_media_file(api_key, filename)
            return {"media_id": media_id}, 201
        else:
            return restrictions_details

    @staticmethod
    async def delete_tweet(api_key: str, tweet_id: int) \
            -> tuple[Optional[dict], int]:
        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            deleted_details = await Tweet.delete_tweet(api_key, tweet_id)
            if deleted_details:
                if len(deleted_details) == 2:
                    await MediaFile.delete_bulk_media_file(
                        user_name=api_key,
                        files_ids=deleted_details[1])

                    # try asyncio to thread

                    # await asyncio_to_thread(
                    #     MediaFile.delete_bulk_media_file,
                    #     user_name=api_key,
                    #     files_ids=deleted_details[1])

                    # Make separate func for the above + delete file in container media files

                return None, 200
            else:
                error_message["error_type"] = "Unauthorized"
            error_message["error_message"] = "You can delete only yours tweet!"
            return error_message, 401
        else:
            return restrictions_details

    @staticmethod
    async def dislike_tweet_by_id(api_key: str, tweet_id: int) \
            -> tuple[Optional[dict], int]:
        restrictions_details = (
            await HandleEndpoint._like_dislike_tweet_check(api_key, tweet_id)
        )
        if not restrictions_details:
            tweet_like_id = await TweetLike.dislike_tweet(api_key, tweet_id)
            if tweet_like_id:
                return None, 201
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = "You did not like the tweet!"
                return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def like_tweet_by_id(api_key: str, tweet_id: int) \
            -> tuple[Optional[dict], int]:
        restrictions_details = (
            await HandleEndpoint._like_dislike_tweet_check(api_key, tweet_id)
        )
        if not restrictions_details:
            tweet_like_id = await TweetLike.like_tweet(api_key, tweet_id)
            if tweet_like_id:
                return None, 201
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    "You have already liked the tweet!"
                )
                return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def get_tweet_feed(api_key: str) -> tuple[Optional[dict], int]:
        user = await User.get_user_by_name(api_key)
        if user:
            followed_users_name = list()
            tweet_feed = list()
            for i_followed in user.followed:
                followed_users_name.append(i_followed.name)
            if followed_users_name:
                tweets = await Tweet.get_tweets_by_author(followed_users_name)
                if tweets:
                    tweet_feed = await HandleEndpoint._create_tweet_feed(tweets)
            response_message = {"result": True, "tweets": tweet_feed}
            return response_message, 200

        else:
            error_message["error_type"] = "Unauthorized"
            error_message["error_message"] = (
                "You don't have permission for operation!"
            )
            return error_message, 400

    @staticmethod
    async def get_user_profile_details(api_key: str, user_id: int) \
            -> tuple[dict, int]:

        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            user = await User.get_user_by_id(user_id)
            if user:
                user_profile = await asyncio_to_thread(
                    HandleEndpoint._create_user_profile,
                    user,
                )
                response_message = {"result": True, "user": user_profile}
                return response_message, 200
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    f"There is no user with id: {user_id} in db."
                )
                return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def get_own_profile_details(api_key: str) -> tuple[dict, int]:

        restrictions_details = await HandleEndpoint._permission_check(api_key)
        if not restrictions_details:
            user = await User.get_user_by_name(api_key)
            if user:
                user_profile = await asyncio_to_thread(
                    HandleEndpoint._create_user_profile,
                    user,
                )
                response_message = {"result": True, "user": user_profile}
                return response_message, 200
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    f"There is no details in database! Try again!"
                )
                return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def follow_other_user(api_key: str, followed_id: int) \
            -> tuple[Optional[dict], int]:
        restrictions_details = await (
            HandleEndpoint._follow_unfollow_check(api_key, followed_id)
        )
        if not restrictions_details:
            user_id = await User.get_user_id_by_name(api_key)
            follow_details = await User.follow_other_user(user_id, followed_id)
            if follow_details:
                return None, 201
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    f"You have already followed this user!"
                )
            return error_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def unfollow_user(api_key: str, followed_id: int) \
            -> tuple[Optional[dict], int]:
        restrictions_details = await (
            HandleEndpoint._follow_unfollow_check(api_key, followed_id)
        )
        if not restrictions_details:
            user_id = await User.get_user_id_by_name(api_key)
            unfollow_details = await User.unfollow_user(user_id, followed_id)
            if unfollow_details:
                return None, 201
            else:
                error_message["error_type"] = "Bad Request"
                error_message["error_message"] = (
                    f"You are not following this user!"
                )
            return error_message, 400
        else:
            return restrictions_details
