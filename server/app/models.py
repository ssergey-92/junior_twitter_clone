from datetime import datetime
from os import path as os_path
from random import randint
from re import findall
from typing import Optional, Union

from aiofiles import open as aio_open, os as aio_os
from fastapi import UploadFile

from database import User, MediaFile, Tweet, TweetLike
from schemas import AddTweetIn

IMAGES_PATH = "/usr/share/nginx/html/images"
ALLOWED_IMAGE_EXTENSIONS = ("png", "jpg", "jpeg")
error_template_message = {
    "result": False,
    "error_type": "",
    "error_message": ""
}

FORBIDDEN_MESSAGE = {
    "result": False,
    "error_type": "Forbidden",
    "error_message": "You don't have permission for such operation!"
    }
FORBIDDEN_RESPONSE = (FORBIDDEN_MESSAGE, 403,)


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
                {"id": i_follower.id, "name": i_follower.name}
            )
        for i_followed in user.followed:
            user_profile["following"].append(
                {"id": i_followed.id, "name": i_followed.name}
            )

        return user_profile

    @staticmethod
    def _check_media_file(file_name: str) \
            -> Union[tuple[dict, int], str, None]:
        split_file_name = file_name.rsplit('.')
        if split_file_name[-1:] not in ALLOWED_IMAGE_EXTENSIONS:
            error_template_message["error_type"] = "Bad Request"
            error_template_message["error_message"] = (
                    f"Support only filename formats: "
                    f"{ALLOWED_IMAGE_EXTENSIONS}!"
                )
            return error_template_message, 400
        elif (len(split_file_name) != 2 or
                not findall(r"^[\w_]+$", split_file_name[0])):
            safe_filename = "{name}.{format}".format(
                name=randint(1, 1000),
                format=split_file_name[-1:]
            )
            return safe_filename
        else:
            return None



    @staticmethod
    async def _create_tweet_feed(tweets: list[Tweet]) -> list:
        tweet_feed = list()
        for i_tweet in tweets:
            if not i_tweet.tweet_media_ids:
                attachments = list()
            else:
                attachments = await MediaFile.get_media_files_names(
                    i_tweet.tweet_media_ids
                )
            tweet_details = {
                "id": i_tweet.id,
                "content": i_tweet.tweet_data,
                "attachments": attachments,
                "author":
                    {"id": i_tweet.author.id, "name": i_tweet.author.name},
                "likes": list()
            }
            for i_like in i_tweet.likes:
                like_details = {
                    "user_id": i_like.user_details.id,
                    "name": i_like.user_details.name,
                }
                tweet_details["likes"].append(like_details)
            tweet_feed.append(tweet_details)
        return tweet_feed

    @staticmethod
    async def _permission_check(api_key: str) -> Optional[tuple[dict, int]]:
        if not await User.is_existed_user_name(api_key):
            error_template_message["error_type"] = "Unauthorized"
            error_template_message["error_message"] = (
                "You don't have permission for operation!"
            )
            return error_template_message, 400
        else:
            return None

    @staticmethod
    async def _follow_unfollow_check(api_key: str, followed_id: int) \
            -> Optional[tuple[dict, int]]:
        permission_restrictions = await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            if await User.is_existed_user_id(followed_id):
                return None
            else:
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = (
                    f"Followed user with id: {followed_id} is not existed"
                )
            return error_template_message, 400
        else:
            return permission_restrictions

    @staticmethod
    async def _like_dislike_tweet_check(api_key: str, tweet_id: int) \
            -> Optional[tuple[dict, int]]:
        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            tweet_existed = await Tweet.is_existed(tweet_id)
            if tweet_existed:
                return None
            else:
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = (
                    f"Tweet with id: {tweet_id} is not existed"
                )
            return error_template_message, 400
        else:
            return permission_restrictions

    @staticmethod
    async def _delete_files_from_sys(media_files_names: list, path: str)\
            -> None:
        for i_media_file in media_files_names:
            await aio_os.remove(os_path.join(path, i_media_file))

    @staticmethod
    async def _delete_media_files(api_key: str, files_ids: list) -> None:
        deleted_file_names_from_db = await MediaFile.bulk_delete(
                user_name=api_key,
                files_ids=files_ids
            )
        await HandleEndpoint._delete_files_from_sys(
                deleted_file_names_from_db,
                IMAGES_PATH
            )

    @staticmethod
    async def _save_media_file_in_sys(
            media_file: UploadFile,
            unique_filename: str) -> None:
        media_file_path = os_path.join(IMAGES_PATH, unique_filename)
        async with aio_open(media_file_path, 'wb') as out_file:
            media_file_data = await media_file.read()
            await out_file.write(media_file_data)

    @staticmethod
    async def add_tweet(api_key: str, new_tweet: AddTweetIn) \
            -> tuple[dict, int]:
        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            new_tweet_details = dict(new_tweet)
            tweet_id = await Tweet.add_tweet(
                **new_tweet_details,
                author_name=api_key
            )
            return {"tweet_id": tweet_id}, 201
        else:
            return permission_restrictions

    @staticmethod
    async def add_media_file(api_key: str, file: UploadFile) \
            -> tuple[dict, int]:
        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            file_restrictions = HandleEndpoint._check_media_file(file.filename)
            if not file_restrictions:
                unique_filename = '{datetime}_{name}'.format(
                    datetime=datetime.now().strftime('%d%b%y%H%M%S'),
                    name=file.filename
                )
                await HandleEndpoint._save_media_file_in_sys(
                    file, unique_filename
                )
                media_id = await MediaFile.add_media_file(
                    api_key, unique_filename
                )
                return {"media_id": media_id}, 201
            else:
                return file_restrictions
        return permission_restrictions

    @staticmethod
    async def delete_tweet(api_key: str, tweet_id: int) \
            -> tuple[Optional[dict], int]:
        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            deleted_details = await Tweet.delete_tweet(api_key, tweet_id)
            if deleted_details:
                if len(deleted_details) == 2 and deleted_details[1]:
                    await HandleEndpoint._delete_media_files(
                        api_key,
                        deleted_details[1]
                    )
                return None, 200
            else:
                error_template_message["error_type"] = "Unauthorized"
            error_template_message["error_message"] = "You can delete only yours tweet!"
            return error_template_message, 401
        else:
            return permission_restrictions

    @staticmethod
    async def dislike_tweet_by_id(api_key: str, tweet_id: int) \
            -> tuple[Optional[dict], int]:
        permission_restrictions = (
            await HandleEndpoint._like_dislike_tweet_check(api_key, tweet_id)
        )
        if not permission_restrictions:
            tweet_like_id = await TweetLike.dislike_tweet(api_key, tweet_id)
            if tweet_like_id:
                return None, 201
            else:
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = "You did not like the tweet!"
                return error_template_message, 400
        else:
            return permission_restrictions

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
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = (
                    "You have already liked the tweet!"
                )
                return error_template_message, 400
        else:
            return restrictions_details

    @staticmethod
    async def get_user_tweet_feed(api_key: str) -> tuple[dict, int]:
        user = await User.get_user_by_name(api_key)
        if user:
            followed_users_name = list()
            tweet_feed = list()
            for i_followed in user.followed:
                followed_users_name.append(i_followed.name)
            if followed_users_name:
                tweets = await Tweet.get_tweets_by_author_sorted_by_likes(
                    followed_users_name)
                if tweets:
                    tweet_feed = await HandleEndpoint._create_tweet_feed(
                        tweets)
            response_message = {"result": True, "tweets": tweet_feed}
            return response_message, 200

        else:
            error_template_message["error_type"] = "Unauthorized"
            error_template_message["error_message"] = (
                "You don't have permission for operation!"
            )
            return error_template_message, 400

    @staticmethod
    async def get_full_tweet_feed(api_key: str) -> tuple[dict, int]:
        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            tweets = await Tweet.get_all_tweets_sorted_by_likes()
            if tweets:
                tweet_feed = await HandleEndpoint._create_tweet_feed(
                    tweets)
            else:
                tweet_feed = list()
            response_message = {"result": True, "tweets": tweet_feed}
            return response_message, 200
        else:
            return permission_restrictions

    @staticmethod
    async def get_user_profile_details(api_key: str, user_id: int) \
            -> tuple[dict, int]:

        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            user = await User.get_user_by_id(user_id)
            if user:
                user_profile = HandleEndpoint._create_user_profile(user)
                response_message = {"result": True, "user": user_profile}
                return response_message, 200
            else:
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = (
                    f"There is no user with id: {user_id} in db."
                )
                return error_template_message, 400
        else:
            return permission_restrictions

    @staticmethod
    async def get_own_profile_details(api_key: str) -> tuple[dict, int]:
        permission_restrictions = \
            await HandleEndpoint._permission_check(api_key)
        if not permission_restrictions:
            user = await User.get_user_by_name(api_key)
            user_profile = HandleEndpoint._create_user_profile(user)
            response_message = {"result": True, "user": user_profile}
            return response_message, 200
        else:
            return permission_restrictions

    @staticmethod
    async def follow_other_user(api_key: str, followed_id: int) \
            -> tuple[Optional[dict], int]:
        permission_restrictions = await (
            HandleEndpoint._follow_unfollow_check(api_key, followed_id)
        )
        if not permission_restrictions:
            user_id = await User.get_user_id_by_name(api_key)
            follow_details = await User.follow_other_user(user_id, followed_id)
            if follow_details:
                return None, 201
            else:
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = (
                    f"You have already followed this user!"
                )
            return error_template_message, 400
        else:
            return permission_restrictions

    @staticmethod
    async def unfollow_user(api_key: str, followed_id: int) \
            -> tuple[Optional[dict], int]:
        permission_restrictions = await (
            HandleEndpoint._follow_unfollow_check(api_key, followed_id)
        )
        if not permission_restrictions:
            user_id = await User.get_user_id_by_name(api_key)
            unfollow_details = await User.unfollow_user(user_id, followed_id)
            if unfollow_details:
                return None, 201
            else:
                error_template_message["error_type"] = "Bad Request"
                error_template_message["error_message"] = (
                    f"You are not following this user!"
                )
            return error_template_message, 400
        else:
            return permission_restrictions
