"""Module for handling logic for media file."""

from datetime import datetime
from os import path as os_path
from random import randint
from re import findall

from aiofiles import open as aio_open
from aiofiles import os as aio_os
from fastapi import UploadFile

from app.models.media_files import MediaFile
from common import create_bad_request_response, get_save_media_files_path

SUPPORTED_MEDIA_EXTENSIONS = ("png", "jpg", "jpeg")
error_message = {"result": False, "error_type": "", "error_message": ""}


def make_safe_file_name(file_name: str) -> str:
    """Check filename.

    If file name has english letters, numbers and underscore, return same
    name. Else return file name as random number from 1 to 1000.

    Args:
        file_name (str): file name

    Returns:
        str : safe file name

    """
    split_file_name = file_name.rsplit(".")
    allowed_symbols = findall(r"^[\w_]+$", split_file_name[0])
    if len(split_file_name) == 2 and allowed_symbols:
        return file_name
    safe_filename = "{name}.{format}".format(
        name=randint(1, 1000), format=split_file_name[-1],
    )
    return safe_filename


def is_supported_media_file_extension(file_name: str) -> bool:
    """Check if file has supported extension.

    Args:
        file_name (str): file name

    Returns:
        bool : True if supported else False

    """
    split_name = file_name.rsplit(".")
    extension = split_name[-1]
    return len(split_name) > 1 and extension in SUPPORTED_MEDIA_EXTENSIONS


async def save_media_file_in_sys(
    media_file: UploadFile, unique_filename: str,
) -> None:
    """Save media file in system.

    Args:
        media_file (UploadFile): file data
        unique_filename (str): unique file name

    """
    media_files_path = get_save_media_files_path()
    file_abs_path = os_path.join(media_files_path, unique_filename)
    async with aio_open(file_abs_path, "wb") as out_file:
        media_file_data = await media_file.read()
        await out_file.write(media_file_data)


async def delete_media_files_from_sys(media_files_names: list) -> None:
    """Delete media files from system.

    Args:
        media_files_names (list): list of file names

    """
    media_files_path = get_save_media_files_path()
    for i_media_file in media_files_names:
        await aio_os.remove(os_path.join(media_files_path, i_media_file))


async def delete_media_files(api_key: str, files_ids: list) -> None:
    """Delete media files from database and system.

    Args:
        api_key (str): username
        files_ids (list): list of files ids

    """
    deleted_file_names_from_db = await MediaFile.bulk_delete(
        user_name=api_key, files_ids=files_ids,
    )
    if deleted_file_names_from_db:
        await delete_media_files_from_sys(deleted_file_names_from_db)


async def add_media_file(
    api_key: str, media_file: UploadFile,
) -> tuple[dict, int]:
    """Handle logic of add media file endpoint.

    Check if file name is existed and file extension is supported then
    create unique file name and save it system and its details id db.
    Then return success response details. Else return corresponding
    response with error.

    Args:
        api_key (str): username
        media_file (UploadFile): media file data

    Returns:
        tuple[dict, int]: response message and status code

    """
    filename = media_file.filename
    if not filename:
        return create_bad_request_response("File name should be set!")
    elif not is_supported_media_file_extension(filename):
        return create_bad_request_response(
            f"Support only media formats: {SUPPORTED_MEDIA_EXTENSIONS}!",
        )
    safe_filename = make_safe_file_name(filename)
    unique_filename = "{datetime}_{name}".format(
        datetime=datetime.now().strftime("%d%b%y%H%M%S"),
        name=safe_filename,
    )
    await save_media_file_in_sys(media_file, unique_filename)
    media_id = await MediaFile.add_media_file(api_key, unique_filename)
    return {"media_id": media_id}, 201
