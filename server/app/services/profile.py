"""Module for handling logic for profiles."""

from app.models.users import User
from common import create_bad_request_response, create_unregister_response


def create_user_profile(user: User) -> dict:
    """Create user profile from 'User'.

    Args:
        user (User): user details

    Returns:
        dict : user profile

    """
    user_followers = []
    user_followed = []
    for i_follower in user.followers:
        user_followers.append({"id": i_follower.id, "name": i_follower.name})
    for i_followed in user.followed:
        user_followed.append({"id": i_followed.id, "name": i_followed.name})
    user_profile = {
        "id": user.id,
        "name": user.name,
        "followers": user_followers,
        "following": user_followed,
    }
    return user_profile


async def get_user_profile(user_id: int) -> tuple[dict, int]:
    """Handle logic of get user profile endpoint.

    Check if user 'user_id'is existed then create user profile and return
    success response details. Else return response with error.

    Args:
        user_id (int): user id

    Returns:
        tuple[dict, int]: response message and status code

    """
    user = await User.get_user_by_id(user_id)
    if not user:
        return create_bad_request_response(
            f"There is no user with id: {user_id} in db.",
        )
    user_profile = create_user_profile(user)
    response_message = {"result": True, "user": user_profile}
    return response_message, 200


async def get_own_profile(api_key: str) -> tuple[dict, int]:
    """Handle logic of get own profile endpoint.

    Check if user 'api_key' is existed then create user profile and return
    success response details. Else return response with error.

    Args:
        api_key (str): username

    Returns:
        tuple[dict, int]: response message and status code

    """
    user = await User.get_user_by_name(api_key)
    if not user:
        return create_unregister_response()
    user_profile = create_user_profile(user)
    response_message = {"result": True, "user": user_profile}
    return response_message, 200
