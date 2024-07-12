"""Module for testing common services from app/services/common.py."""

from os import environ as os_environ

from pytest import raises as pytest_raises

from ..app.services import common
from .common import (
    BAD_REQUEST_STATUS_CODE,
    ERROR_MESSAGE,
    FORBIDDEN_STATUS_CODE,
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


class TestServicesCommon:
    @staticmethod
    def test_get_get_save_media_files_path(
            add_paths_to_os_environ: None,
            reset_os_environ_paths: None,
    ) -> None:
        assert isinstance(common.get_save_media_files_path(), str)
        os_environ.pop("SAVE_MEDIA_PATH")
        with pytest_raises(SystemExit):
            common.get_save_media_files_path()

    @staticmethod
    def test_create_unregister_response() -> None:
        message, status_code = common.create_unregister_response()
        assert status_code == unregister_response["status_code"]
        assert message.keys() == unregister_response["message"].keys()
        assert message["result"] == unregister_response["message"]["result"]
        assert isinstance(message["error_type"], str)
        assert isinstance(message["error_message"], str)

    @staticmethod
    def test_create_bad_request_response() -> None:
        error_details = "bad request details"
        message, status_code = common.create_bad_request_response(
            error_details,
        )
        assert status_code == bad_request_response["status_code"]
        assert message.keys() == bad_request_response["message"].keys()
        assert message["result"] == bad_request_response["message"]["result"]
        assert message["error_message"] == error_details
        assert isinstance(message["error_type"], str)

    @staticmethod
    def test_create_forbidden_response() -> None:
        error_details = "forbidden details"
        message, status_code = common.create_forbidden_response(
            error_details,
        )
        assert status_code == forbidden_response["status_code"]
        assert message.keys() == forbidden_response["message"].keys()
        assert message["result"] == forbidden_response["message"]["result"]
        assert message["error_message"] == error_details
        assert isinstance(message["error_type"], str)
