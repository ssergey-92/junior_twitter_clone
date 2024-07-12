"""Module for handling logic with user."""

from typing import Optional

from common import create_unregister_response, create_bad_request_response
from app.models.users import User


async def follow_other_user(
    api_key: str, followed_id: int,
) -> tuple[Optional[dict], int]:
    """Handle logic of follow other user endpoint.

    Check if users 'api_key' and 'followed_id' is existed and user has not
    already followed him. If so, make entry in db and return success
    response details. Else return corresponding response with error.

    Args:
        api_key (str): username
        followed_id (int): followed user id

    Returns:
        tuple[dict, int]: response message and status code

    """
    own_id = await User.get_user_id_by_name(api_key)
    if not own_id:
        return create_unregister_response()
    elif not await User.get_user_by_id(followed_id):
        return create_bad_request_response("Followed user is not exist!")
    elif not await User.follow_other_user(own_id, followed_id):
        return create_bad_request_response(
            "You have already followed this user!",
        )

    return None, 201


async def unfollow_user(
    api_key: str, followed_id: int,
) -> tuple[Optional[dict], int]:
    """Handle logic of unfollow user endpoint.

    Check if users 'api_key' and 'followed_id' is existed and user has
    already followed him. If so, make entry in db and return success
    response details. Else return corresponding response with error.

    Args:
        api_key (str): username
        followed_id (int): followed user id

    Returns:
        tuple[dict, int]: response message and status code

    """
    own_id = await User.get_user_id_by_name(api_key)
    if not own_id:
        return create_unregister_response()
    elif not await User.get_user_by_id(followed_id):
        return create_bad_request_response("Followed user is not exist!")
    elif not await User.unfollow_user(own_id, followed_id):
        return create_bad_request_response("You are not following this user!")

    return None, 201
