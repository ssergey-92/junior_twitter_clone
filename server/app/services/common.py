"""Module with common functions for services package."""

from os import environ as os_environ
from sys import exit as sys_exit

error_message = {"result": False, "error_type": "", "error_message": ""}


def get_save_media_files_path() -> str:
    """Get sve media path.

    Return save media path from os.environ if key  'SAVE_MEDIA_PATH' is
    existed. Else call system exit function.


    Returns:
        str : save media path

    """
    media_files_path = os_environ.get("SAVE_MEDIA_PATH", None)
    if media_files_path:
        return media_files_path
    else:
        sys_exit("SAVE_MEDIA_PATH should be set to run the program!")


def create_unregister_response() -> tuple[dict, int]:
    """Create unregister response.

    Returns:
        tuple[dict, int] : response message and http status code

    """
    error_message["error_type"] = "Bad Request"
    error_message["error_message"] = "You are not register in system!"
    return error_message, 400


def create_bad_request_response(error_details: str) -> tuple[dict, int]:
    """Create bad request response.

    Args:
        error_details (str): details of error message

    Returns:
        tuple[dict, int] : response message and http status code

    """
    error_message["error_type"] = "Bad Request"
    error_message["error_message"] = error_details
    return error_message, 400


def create_forbidden_response(error_details: str) -> tuple[dict, int]:
    """Create forbidden response.

    Args:
        error_details (str): details of error message

    Returns:
        tuple[dict, int] : response message and http status code

    """
    error_message["error_type"] = "Forbidden"
    error_message["error_message"] = error_details
    return error_message, 403
