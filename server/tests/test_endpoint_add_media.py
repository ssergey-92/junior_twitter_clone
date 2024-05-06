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

ADD_MEDIA_ENDPOINT = FAKE_TWITTER_ENDPOINTS["add_media"]["endpoint"]
ADD_MEDIA_HTTP_METHOD = FAKE_TWITTER_ENDPOINTS["add_media"]["http_method"]
CORRECT_BODY_WITH_FILE_NAME_FOR_RENAME = {
    "file": open_test_image(MEDIA_FILE_NAME_FOR_RENAME)
}
CORRECT_BODY_WITH_UNSUPPORTED_FILE_EXTENSION = [
    {"file": open_test_image(MEDIA_FILE_UNSUPPORTED_FORMAT)}
]
CORRECT_MEDIA_BODY_DATA_AND_RESPONSE = (
    ({"file": open_test_image(FILE_NAME_1)}, {"result": True, "media_id": 4}),
    ({"file": open_test_image(FILE_NAME_2)}, {"result": True, "media_id": 5}),
    ({"file": open_test_image(FILE_NAME_3)}, {"result": True, "media_id": 6}),
    (CORRECT_BODY_WITH_FILE_NAME_FOR_RENAME, {"result": True, "media_id": 7}),
)
INCORRECT_MEDIA_BODY_DATA = (
    {},
    {"file": None},
    {"other_name": open_test_image(FILE_NAME_1)},
)


class TestAddMediaEndpoint:

    @staticmethod
    @pytest_mark.asyncio
    async def test_validation_handler_for_incorrect_request_form(
        client: AsyncClient,
    ) -> None:
        for i_data in INCORRECT_MEDIA_BODY_DATA:
            response = await client.request(
                method=ADD_MEDIA_HTTP_METHOD,
                url=ADD_MEDIA_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                files=i_data,
            )
            response_data = response.json()
            assert response.status_code == BAD_REQUEST_STATUS_CODE
            assert response_data.get("result", None) == ERROR_MESSAGE["result"]
            assert response_data.keys() == ERROR_MESSAGE.keys()
            assert isinstance(response_data.get("error_type", None), str)
            assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_unsupported_media_file_format(
        client: AsyncClient, init_test_data_for_db: None
    ) -> None:
        for i_data in CORRECT_BODY_WITH_UNSUPPORTED_FILE_EXTENSION:
            response = await client.request(
                method=ADD_MEDIA_HTTP_METHOD,
                url=ADD_MEDIA_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                files=i_data,
            )
            response_data = response.json()
            assert response.status_code == BAD_REQUEST_STATUS_CODE
            assert response_data.get("result", None) == ERROR_MESSAGE["result"]
            assert response_data.keys() == ERROR_MESSAGE.keys()
            assert isinstance(response_data.get("error_type", None), str)
            assert isinstance(response_data.get("error_message", None), str)

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_for_correct_response(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_test_folders: None,
    ) -> None:
        for i_data in CORRECT_MEDIA_BODY_DATA_AND_RESPONSE:
            response = await client.request(
                method=ADD_MEDIA_HTTP_METHOD,
                url=ADD_MEDIA_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                files=i_data[0],
            )
            assert response.json() == i_data[1]
            assert response.status_code == CREATED_STATUS_CODE

    @staticmethod
    @pytest_mark.asyncio
    async def test_endpoint_that_media_is_saved_in_sys(
        client: AsyncClient,
        init_test_data_for_db: None,
        init_test_folders: None,
    ) -> None:
        before_total_images = len(os_listdir(SAVE_MEDIA_ABS_PATH))
        await client.request(
            method=ADD_MEDIA_HTTP_METHOD,
            url=ADD_MEDIA_ENDPOINT,
            headers=AUTHORIZED_HEADER,
            files=CORRECT_MEDIA_BODY_DATA_AND_RESPONSE[0][0],
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
        for i_data in CORRECT_MEDIA_BODY_DATA_AND_RESPONSE:
            await client.request(
                method=ADD_MEDIA_HTTP_METHOD,
                url=ADD_MEDIA_ENDPOINT,
                headers=AUTHORIZED_HEADER,
                files=CORRECT_BODY_WITH_FILE_NAME_FOR_RENAME,
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
            method=ADD_MEDIA_HTTP_METHOD,
            url=ADD_MEDIA_ENDPOINT,
            headers=AUTHORIZED_HEADER,
            files=CORRECT_MEDIA_BODY_DATA_AND_RESPONSE[0][0],
        )
        after_total_media = await MediaFile.get_total_media_files()
        assert before_total_media + 1 == after_total_media
