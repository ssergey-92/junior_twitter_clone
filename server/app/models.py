from datetime import datetime
from os import environ as os_environ
from os import path as os_path
from random import randint
from re import findall
from sys import exit as sys_exit
from typing import Optional

from aiofiles import open as aio_open
from aiofiles import os as aio_os
from fastapi import UploadFile

from database import MediaFile, Tweet, TweetLike, User
from schemas import AddTweetIn

SUPPORTED_MEDIA_EXTENSIONS = ("png", "jpg", "jpeg")
error_message = {"result": False, "error_type": "", "error_message": ""}


class HandleEndpoint:

    @staticmethod
    async def add_tweet(
        api_key: str, new_tweet: AddTweetIn,
    ) -> tuple[dict, int]:
        new_tweet_details = dict(new_tweet)
        tweet_id = await Tweet.add_tweet(
            **new_tweet_details, author_name=api_key,
        )
        return {"tweet_id": tweet_id}, 201

    @staticmethod
    async def add_media_file(
        api_key: str, media_file: UploadFile,
    ) -> tuple[dict, int]:
        filename = media_file.filename
        if not filename:
            return HandleEndpoint._create_bad_request_response(
                "File name should be set!",
            )
        elif not HandleEndpoint._is_supported_media_file_extension(filename):
            return HandleEndpoint._create_bad_request_response(
                f"Support only media formats: {SUPPORTED_MEDIA_EXTENSIONS}!",
            )
        safe_filename = HandleEndpoint._make_safe_file_name(filename)
        unique_filename = "{datetime}_{name}".format(
            datetime=datetime.now().strftime("%d%b%y%H%M%S"),
            name=safe_filename,
        )
        await HandleEndpoint._save_media_file_in_sys(
            media_file, unique_filename,
        )
        media_id = await MediaFile.add_media_file(api_key, unique_filename)
        return {"media_id": media_id}, 201

    @staticmethod
    async def delete_tweet(
        api_key: str, tweet_id: int,
    ) -> tuple[Optional[dict], int]:
        deleted_details = await Tweet.delete_tweet(api_key, tweet_id)
        if not deleted_details:
            return HandleEndpoint._create_forbidden_response(
                "You can delete only yours tweet which is posted!",
            )
        media_files_ids = deleted_details[1]
        if media_files_ids:
            await HandleEndpoint._delete_media_files(
                api_key, media_files_ids,
            )

        return None, 200

    @staticmethod
    async def dislike_tweet_by_id(
        api_key: str, tweet_id: int,
    ) -> tuple[Optional[dict], int]:
        tweet_like_id = await TweetLike.dislike_tweet(api_key, tweet_id)
        if not tweet_like_id:
            return HandleEndpoint._create_bad_request_response(
                "You did not like the tweet!",
            )

        return None, 201

    @staticmethod
    async def like_tweet_by_id(
        api_key: str, tweet_id: int,
    ) -> tuple[Optional[dict], int]:
        tweet_like_id = await TweetLike.like_tweet(api_key, tweet_id)
        if not tweet_like_id:
            return HandleEndpoint._create_bad_request_response(
                "You have already liked the tweet!",
            )

        return None, 201

    # @staticmethod
    # async def get_user_tweet_feed(api_key: str) -> tuple[dict, int]:
    #     user = await User.get_user_by_name(api_key)
    #     if not user:
    #         return HandleEndpoint._create_unregister_response()
    #     followed_users_name = []
    #     tweet_feed = []
    #     for i_followed in user.followed:
    #         followed_users_name.append(i_followed.name)
    #     if followed_users_name:
    #         tweets = await Tweet.get_tweets_by_author_sorted_by_likes(
    #             followed_users_name,
    #         )
    #         if tweets:
    #             tweet_feed = await HandleEndpoint._create_tweet_feed(
    #                 tweets,
    #             )
    #     response_message = {"result": True, "tweets": tweet_feed}
    #     return response_message, 200

    @staticmethod
    async def get_full_tweet_feed() -> tuple[dict, int]:
        tweets = await Tweet.get_all_tweets_sorted_by_likes()
        tweet_feed = []
        if tweets:
            tweet_feed = await HandleEndpoint._create_tweet_feed(tweets)
        response_message = {"result": True, "tweets": tweet_feed}
        return response_message, 200

    @staticmethod
    async def get_user_profile_details(user_id: int) -> tuple[dict, int]:
        user = await User.get_user_by_id(user_id)
        if not user:
            return HandleEndpoint._create_bad_request_response(
                f"There is no user with id: {user_id} in db.",
            )
        user_profile = HandleEndpoint._create_user_profile(user)
        response_message = {"result": True, "user": user_profile}
        return response_message, 200

    @staticmethod
    async def get_own_profile_details(api_key: str) -> tuple[dict, int]:
        user = await User.get_user_by_name(api_key)
        if not user:
            return HandleEndpoint._create_unregister_response()
        user_profile = HandleEndpoint._create_user_profile(user)
        response_message = {"result": True, "user": user_profile}
        return response_message, 200

    @staticmethod
    async def follow_other_user(
        api_key: str, followed_id: int,
    ) -> tuple[Optional[dict], int]:
        own_id = await User.get_user_id_by_name(api_key)
        if not own_id:
            return HandleEndpoint._create_unregister_response()
        elif not await User.follow_other_user(own_id, followed_id):
            return HandleEndpoint._create_bad_request_response(
                "You have already followed this user!",
            )

        return None, 201

    @staticmethod
    async def unfollow_user(
        api_key: str, followed_id: int,
    ) -> tuple[Optional[dict], int]:
        own_id = await User.get_user_id_by_name(api_key)
        if not own_id:
            return HandleEndpoint._create_unregister_response()
        elif not await User.unfollow_user(own_id, followed_id):
            return HandleEndpoint._create_bad_request_response(
                "You are not following this user!",
            )

        return None, 201

    @staticmethod
    def _create_user_profile(user: User) -> dict:
        user_followers = []
        user_followed = []
        for i_follower in user.followers:
            user_followers.append(
                {"id": i_follower.id, "name": i_follower.name},
            )
        for i_followed in user.followed:
            user_followed.append(
                {"id": i_followed.id, "name": i_followed.name},
            )
        user_profile = {
            "id": user.id,
            "name": user.name,
            "followers": user_followers,
            "following": user_followed,
        }
        return user_profile

    @staticmethod
    def _is_supported_media_file_extension(file_name: str) -> bool:
        split_name = file_name.rsplit(".")
        extension = split_name[-1]
        return len(split_name) > 1 and extension in SUPPORTED_MEDIA_EXTENSIONS

    @staticmethod
    def _make_safe_file_name(file_name: str) -> str:
        split_file_name = file_name.rsplit(".")
        allowed_symbols = findall(r"^[\w_]+$", split_file_name[0])
        if len(split_file_name) == 2 and allowed_symbols:
            return file_name
        safe_filename = "{name}.{format}".format(
            name=randint(1, 1000), format=split_file_name[-1],
        )
        return safe_filename

    @staticmethod
    async def _create_tweet_feed(tweets: list[Tweet]) -> list:
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

    @staticmethod
    def _get_save_media_files_path() -> str:
        media_files_path = os_environ.get("SAVE_MEDIA_PATH", None)
        if media_files_path:
            return media_files_path
        else:
            sys_exit("SAVE_MEDIA_PATH should be set to run the program!")

    @staticmethod
    async def _delete_files_from_sys(media_files_names: list) -> None:
        media_files_path = HandleEndpoint._get_save_media_files_path()
        for i_media_file in media_files_names:
            await aio_os.remove(os_path.join(media_files_path, i_media_file))

    @staticmethod
    async def _delete_media_files(api_key: str, files_ids: list) -> None:
        deleted_file_names_from_db = await MediaFile.bulk_delete(
            user_name=api_key, files_ids=files_ids,
        )
        if deleted_file_names_from_db:
            await HandleEndpoint._delete_files_from_sys(
                deleted_file_names_from_db,
            )

    @staticmethod
    async def _save_media_file_in_sys(
        media_file: UploadFile, unique_filename: str,
    ) -> None:
        media_files_path = HandleEndpoint._get_save_media_files_path()
        file_abs_path = os_path.join(media_files_path, unique_filename)
        async with aio_open(file_abs_path, "wb") as out_file:
            media_file_data = await media_file.read()
            await out_file.write(media_file_data)

    @staticmethod
    def _create_unregister_response() -> tuple[dict, int]:
        error_message["error_type"] = "Bad Request"
        error_message["error_message"] = (
            "You are not register in system!"
        )
        return error_message, 400

    @staticmethod
    def _create_bad_request_response(error_details: str) -> tuple[dict, int]:
        error_message["error_type"] = "Bad Request"
        error_message["error_message"] = error_details
        return error_message, 400

    @staticmethod
    def _create_forbidden_response(error_details: str) -> tuple[dict, int]:
        error_message["error_type"] = "Forbidden"
        error_message["error_message"] = error_details
        return error_message, 403
