"""Module for testing logic for media file from services/media_file.py ."""

from os import listdir as os_listdir

from fastapi import UploadFile
from pytest import mark as pytest_mark

from ..app.services import media_file
from .common import (
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    FILE_NAME_1,
    FILE_NAME_2,
    FILE_NAME_3,
    FORBIDDEN_STATUS_CODE,
    SAVE_MEDIA_ABS_PATH,
    TWEET_2,
    open_test_image,
    test_user_1,
)

supported_media_files_data = {
    "file_names": (FILE_NAME_1, FILE_NAME_2, FILE_NAME_3),
    "result": True,
}
unsupported_media_files_data = {
    "file_names": ("extension.svg", "extension.pjpeg", "extension.jfif"),
    "result": False,
}
media_files_data = (supported_media_files_data, unsupported_media_files_data)
unsafe_media_file_name = (
    "un.safe.jpg",
    "un'safe.jpg",
    "un}safe.jpg",
)
new_file_name = "new_file_name.jpg"
valid_add_media_files_data = (
    {
        "file": UploadFile(
            filename="new_file.jpg", file=open_test_image(FILE_NAME_1),
        ),
        "api_key": test_user_1["name"],
        "result": {
            "message": {"media_id": 4}, "status_code": CREATED_STATUS_CODE,
        },
    },
)
unregister_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
bad_request_response = {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE,
        }
forbidden_response = {
            "message": ERROR_MESSAGE, "status_code": FORBIDDEN_STATUS_CODE,
        }
invalid_add_media_files_data = (
    {
        "file": UploadFile(
            filename="new_file.ggg", file=open_test_image(FILE_NAME_1),
        ),
        "api_key": test_user_1["name"],
        "result": bad_request_response,
    },
    {
        "file": UploadFile(file=open_test_image(FILE_NAME_1)),
        "api_key": test_user_1["name"],
        "result":  bad_request_response,
    },
)
unexist_user = {
    "id": 0,
    "name": "unexsit_user",
}


class TestServicesMediaFile:

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_media_file(
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        for i_data in valid_add_media_files_data:
            message, status_code = await media_file.add_media_file(
                i_data["api_key"], i_data["file"],
            )
            assert message == i_data["result"]["message"]
            assert status_code == i_data["result"]["status_code"]
        for i_data in invalid_add_media_files_data:
            message, status_code = await media_file.add_media_file(
                i_data["api_key"], i_data["file"],
            )
            assert message.keys() == i_data["result"]["message"].keys()
            assert message["result"] == i_data["result"]["message"]["result"]
            assert status_code == i_data["result"]["status_code"]

    @staticmethod
    def test_check_media_file_extension() -> None:
        for i_media_file_data in media_files_data:
            for i_file_name in i_media_file_data["file_names"]:
                is_supported = (
                    media_file.is_supported_media_file_extension(
                        i_file_name,
                    )
                )
                assert is_supported == i_media_file_data["result"]

    @staticmethod
    def test_make_safe_file_name() -> None:
        for i_file_name in unsafe_media_file_name:
            safe_file_name = media_file.make_safe_file_name(i_file_name)
            safe_file_name = safe_file_name.split(".")
            assert int(safe_file_name[0])
            assert safe_file_name[1] == i_file_name.split(".")[-1]
        for i_file_name in supported_media_files_data["file_names"]:
            safe_file_name = media_file.make_safe_file_name(i_file_name)
            assert safe_file_name == i_file_name

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_media_files_from_sys(
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await media_file.delete_media_files_from_sys(
            [FILE_NAME_1, FILE_NAME_2],
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_delete_media_files(
        add_paths_to_os_environ: None,
        init_test_data_for_db: None,
        init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await media_file.delete_media_files(
            TWEET_2["author_name"], TWEET_2["tweet_media_ids"],
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images - 2 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_save_media_file_in_sys(
        add_paths_to_os_environ: None, init_midia_file_for_test: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        upload_file = UploadFile(
            filename=FILE_NAME_1, file=open_test_image(FILE_NAME_1),
        )
        await media_file.save_media_file_in_sys(
            upload_file, new_file_name,
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images + 1 == after_total_images
