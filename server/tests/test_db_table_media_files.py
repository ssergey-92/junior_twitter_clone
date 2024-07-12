"""Module for testing class MediaFile from app.models.media_files.py ."""

from pytest import mark as pytest_mark

from app.models.media_files import MediaFile
from .common import (
    DEFAULT_TOTAL_MEDIA_FILES,
    MEDIA_FILE_1,
    MEDIA_FILE_2,
    MEDIA_FILE_3,
    test_user_1,
)

new_media_file = {
    "file_name": "new_image.jpg", "user_name": test_user_1["name"],
}
media_files = {
    "ids": [MEDIA_FILE_1["id"], MEDIA_FILE_2["id"], MEDIA_FILE_3["id"]],
    "corresponding_files_names": [
        MEDIA_FILE_1["file_name"],
        MEDIA_FILE_2["file_name"],
        MEDIA_FILE_3["file_name"],
    ],
}
media_files_to_delete = {
    "ids": [MEDIA_FILE_2["id"], MEDIA_FILE_3["id"]],
    "corresponding_files_names": [
        MEDIA_FILE_2["file_name"],
        MEDIA_FILE_3["file_name"],
    ],
    "belongs_to_user": MEDIA_FILE_2["user_name"],
}


class TestMediaFilesMethods:

    @staticmethod
    @pytest_mark.asyncio
    async def test_add_media_files(init_test_data_for_db: None) -> None:
        media_file_id = await MediaFile.add_media_file(**new_media_file)
        assert media_file_id == DEFAULT_TOTAL_MEDIA_FILES + 1

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_total_media_files(init_test_data_for_db: None) -> None:
        total_media_files = await MediaFile.get_total_media_files()
        assert total_media_files == DEFAULT_TOTAL_MEDIA_FILES

    @staticmethod
    @pytest_mark.asyncio
    async def test_get_media_files_names(init_test_data_for_db: None) -> None:
        media_files_names = await MediaFile.get_media_files_names(
            media_files["ids"],
        )
        assert media_files_names == media_files["corresponding_files_names"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_bulk_delete(init_test_data_for_db: None) -> None:
        deleted_media_files_names = await MediaFile.bulk_delete(
            media_files_to_delete["belongs_to_user"],
            media_files_to_delete["ids"],
        )
        assert (deleted_media_files_names ==
                media_files_to_delete["corresponding_files_names"])
