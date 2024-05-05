from os import listdir as os_listdir
from os import path as os_path, environ as os_environ

from fastapi import UploadFile
from pytest import mark as pytest_mark

from ..app.database import User, Tweet
from ..app.models import HandleEndpoint, ALLOWED_IMAGE_EXTENSIONS

from .common_data_for_tests import (
    FILE_NAME_1,
    FILE_NAME_2,
    FILE_NAME_3,
    open_test_image,
    SAVE_MEDIA_ABS_PATH,
    SORTED_TWEET_FEED,
    test_user_1,
    test_user_2,
    TWEET_2
)

ALLOWED_MEDIA_FILES = (FILE_NAME_1, FILE_NAME_2, FILE_NAME_3)
WRONG_MEDIA_FILE_EXTENSIONS = (
    "extension.svg",
    "extension.pjpeg",
    "extension.jfif"
)
UNSAFE_MEDIA_FILE_NAME = (
    "un.safe.jpg",
    "un'safe.jpg",
    "un}safe.jpg",
)
NEW_FILE_NAME = "new_file_name.jpg"

class TestHandleEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_create_user_profile(init_test_data_for_db: None) -> None:
        user = await User.get_user_by_id(test_user_1["id"])
        test_user_profile = test_user_1
        test_user_profile["following"] = test_user_profile.pop("followed")
        assert HandleEndpoint._create_user_profile(user) == test_user_1

    @staticmethod
    def test_check_media_file_extension() -> None:
        for i_media_file in ALLOWED_MEDIA_FILES:
            result = HandleEndpoint._check_media_file_extension(i_media_file)
            assert result is None
        for i_media_file in WRONG_MEDIA_FILE_EXTENSIONS:
            result = HandleEndpoint._check_media_file_extension(i_media_file)
            assert isinstance(result, tuple)

    @staticmethod
    def test_make_safe_file_name() -> None:
        for i_file_name in UNSAFE_MEDIA_FILE_NAME:
            safe_file_name = HandleEndpoint._make_safe_file_name(i_file_name)
            safe_file_name = safe_file_name.split('.')
            assert int(safe_file_name[0])
            assert safe_file_name[1] == i_file_name.split('.')[-1]
        for i_file_name in ALLOWED_MEDIA_FILES:
            safe_file_name = HandleEndpoint._make_safe_file_name(i_file_name)
            assert safe_file_name == i_file_name

    @staticmethod
    @pytest_mark.asyncio
    async def test_create_tweet_feed(init_test_data_for_db: None) -> None:
        all_sorted_tweets = await Tweet.get_all_tweets_sorted_by_likes()
        tweet_feed = await HandleEndpoint._create_tweet_feed(all_sorted_tweets)
        assert tweet_feed == SORTED_TWEET_FEED

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_files_from_sys(
            init_test_data_for_db: None,
            init_midia_file_for_test: None) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await HandleEndpoint._delete_files_from_sys(
            [FILE_NAME_1, FILE_NAME_2], SAVE_MEDIA_ABS_PATH
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_media_files(
            init_test_data_for_db: None,
            init_midia_file_for_test: None) -> None:
        os_environ["SAVE_MEDIA_PATH"] = SAVE_MEDIA_ABS_PATH
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await HandleEndpoint._delete_media_files(
            TWEET_2["author_name"], TWEET_2["tweet_media_ids"]
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_save_media_file_in_sys(
            init_midia_file_for_test: None) -> None:
        os_environ["SAVE_MEDIA_PATH"] = SAVE_MEDIA_ABS_PATH
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        upload_file = UploadFile(
            filename=FILE_NAME_1,
            file=open_test_image(FILE_NAME_1)
        )
        await HandleEndpoint._save_media_file_in_sys(
           upload_file, NEW_FILE_NAME
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images + 1 == after_total_images

