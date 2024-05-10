from os import listdir as os_listdir

from httpx import AsyncClient
from pytest import mark as pytest_mark

from server.app.database import MediaFile

from .common_data_for_tests import (
    AUTHORIZED_HEADER,
    BAD_REQUEST_STATUS_CODE,
    CREATED_STATUS_CODE,
    ERROR_MESSAGE,
    FAKE_TWITTER_ENDPOINTS,
    FILE_NAME_1,
    FILE_NAME_2,
    FILE_NAME_3,
    MEDIA_FILE_NAME_FOR_RENAME,
    MEDIA_FILE_UNSUPPORTED_FORMAT,
    SAVE_MEDIA_ABS_PATH,
    open_test_image,
)

add_media_endpoint = FAKE_TWITTER_ENDPOINTS["add_media"]["endpoint"]
add_media_http_method = FAKE_TWITTER_ENDPOINTS["add_media"]["http_method"]
correct_body_with_file_name_for_rename = {
    "file": open_test_image(MEDIA_FILE_NAME_FOR_RENAME)
}
correct_body_with_unsupported_file_extension = (
    {
        "body": {"file": open_test_image(MEDIA_FILE_UNSUPPORTED_FORMAT)},
        "result": {
            "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE
        }
    },
)
correct_media_body_data_and_response = (
    {
        "body": {"file": open_test_image(FILE_NAME_1)},
        "result": {
            "message": {"result": True, "media_id": 4},
            "status_code": CREATED_STATUS_CODE
        }
    },
    {
        "body": {"file": open_test_image(FILE_NAME_2)},
        "result": {
            "message": {"result": True, "media_id": 5},
            "status_code": CREATED_STATUS_CODE
        }
    },
    {
        "body": {"file": open_test_image(FILE_NAME_3)},
        "result": {
            "message": {"result": True, "media_id": 6},
            "status_code": CREATED_STATUS_CODE}
    },
    {
        "body": correct_body_with_file_name_for_rename,
        "result": {
            "message": {"result": True, "media_id": 7},
            "status_code": CREATED_STATUS_CODE
        }
    },
)
incorrect_media_body_data = {
    "body": ({}, {"file": None}, {"other_name": open_test_image(FILE_NAME_1)}),
    "result": {
        "message": ERROR_MESSAGE, "status_code": BAD_REQUEST_STATUS_CODE
    },
}


class TestAddMediaEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_request_form(
        client: AsyncClient,
    ) -> None:
        for i_body in incorrect_media_body_data["body"]:
            response = await client.request(
                method=add_media_http_method,
                url=add_media_endpoint,
                headers=AUTHORIZED_HEADER,
                files=i_body,
            )
            response_data = response.json()
            assert (response.status_code ==
                    incorrect_media_body_data["result"]["status_code"])
            assert (response_data.keys() ==
                    incorrect_media_body_data["result"]["message"].keys())
            assert response_data.get("result") == ERROR_MESSAGE["result"]
            assert isinstance(response_data.get("error_type"), str)
            assert isinstance(response_data.get("error_message"), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_unsupported_media_file_format(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        for i_data in correct_body_with_unsupported_file_extension:
            response = await client.request(
                method=add_media_http_method,
                url=add_media_endpoint,
                headers=AUTHORIZED_HEADER,
                files=i_data["body"],
            )
            response_data = response.json()
            assert response.status_code == i_data["result"]["status_code"]
            assert response_data.keys() == i_data["result"]["message"].keys()
            assert (response_data.get("result") ==
                    i_data["result"]["message"]["result"])
            assert isinstance(response_data.get("error_type"), str)
            assert isinstance(response_data.get("error_message"), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_test_folders: None,
    ) -> None:
        for i_data in correct_media_body_data_and_response:
            response = await client.request(
                method=add_media_http_method,
                url=add_media_endpoint,
                headers=AUTHORIZED_HEADER,
                files=i_data["body"],
            )
            assert response.json() == i_data["result"]["message"]
            assert response.status_code == i_data["result"]["status_code"]

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_media_is_saved_in_sys(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_test_folders: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await client.request(
            method=add_media_http_method,
            url=add_media_endpoint,
            headers=AUTHORIZED_HEADER,
            files=correct_media_body_data_and_response[0]["body"],
        )
        after_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        assert before_total_images + 1 == after_total_images

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_media_with_unsafe_name_is_renamed(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_test_folders: None,
    ) -> None:
        for i_data in correct_media_body_data_and_response:
            await client.request(
                method=add_media_http_method,
                url=add_media_endpoint,
                headers=AUTHORIZED_HEADER,
                files=correct_body_with_file_name_for_rename,
            )
        for i_file in os_listdir(SAVE_MEDIA_ABS_PATH):
            assert not i_file.endswith(MEDIA_FILE_NAME_FOR_RENAME)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_media_file_name_added_in_db(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_test_folders: None,
    ) -> None:
        before_total_media = await MediaFile.get_total_media_files()
        await client.request(
            method=add_media_http_method,
            url=add_media_endpoint,
            headers=AUTHORIZED_HEADER,
            files=correct_media_body_data_and_response[0]["body"],
        )
        after_total_media = await MediaFile.get_total_media_files()
        assert before_total_media + 1 == after_total_media
