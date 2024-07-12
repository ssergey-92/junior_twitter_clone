"""Module with APIRouter for url startswith api/users ."""

from typing import Annotated, Union

from fastapi import Header, Response, APIRouter

from app.project_logger import project_logger
from app.services import profile, user
from app.schemas import ErrorResponse, UserProfileDetailsOut, SuccessResponse

router = APIRouter()


@router.get(
    path="/api/users/me",
    description="User own profile details",
    responses={
        200: {"description": "OK", "model": UserProfileDetailsOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def get_own_profile_details(
    api_key: Annotated[str, Header()], response: Response,
) -> Union[UserProfileDetailsOut, ErrorResponse]:
    """Endpoint to get own profile.

    Call handler, then set http status code and return response.

    Args:
        api_key (str): username who request own profile
        response (Response): fastapi response model for endpoint

    Returns:
        Union[UserProfileDetailsOut, ErrorResponse]: success get own
        profile or error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=}")
    details, http_code = await profile.get_own_profile(api_key)
    project_logger.info(f"{details=}, {http_code=}")
    response.status_code = http_code
    if http_code == 200:
        return UserProfileDetailsOut(**details)
    return ErrorResponse(**details)


@router.get(
    path="/api/users/{id}",
    description="Get other user profile details by id",
    responses={
        200: {"description": "OK", "model": UserProfileDetailsOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def get_user_profile_details(
    id: int, api_key: Annotated[str, Header()], response: Response,
) -> Union[UserProfileDetailsOut, ErrorResponse]:
    """Endpoint to get user profile.

    Call handler, then set http status code and return response.

    Args:
        id (int): user id whose profile is required
        api_key (str): username who requests user profile
        response (Response): fastapi response model for endpoint

    Returns:
        Union[UserProfileDetailsOut, ErrorResponse]: success get user
        profile or error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=}")
    details, http_code = await profile.get_user_profile(id)
    project_logger.info(f"{details=}, {http_code=}")
    response.status_code = http_code
    if http_code == 200:
        return UserProfileDetailsOut(**details)
    return ErrorResponse(**details)


@router.post(
    path="/api/users/{id}/follow",
    description="Follow user by id",
    responses={
        201: {"description": "Created", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def follow_other_user(
    id: int, api_key: Annotated[str, Header()], response: Response,
) -> Union[SuccessResponse, ErrorResponse]:
    """Endpoint for adding followed user 'id' to user 'api_key'.

    Call handler, then set http status code and return response.

    Args:
        id (int): followed user id
        api_key (str): username whom to add followed user
        response (Response): fastapi response model for endpoint

    Returns:
        Union[SuccessResponse, ErrorResponse]: success adding followed user
            or error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=} | {id=}")
    error_msg, http_code = await user.follow_other_user(api_key, id)
    project_logger.info(f"{error_msg=}, {http_code=}")
    response.status_code = http_code
    if error_msg:
        return ErrorResponse(**error_msg)
    return SuccessResponse()


@router.delete(
    path="/api/users/{id}/follow",
    description="Unsubscribe from user by id",
    responses={
        201: {"description": "Created", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def unfollow_user(
    id: int, api_key: Annotated[str, Header()], response: Response,
) -> Union[SuccessResponse, ErrorResponse]:
    """Endpoint to unfollow user 'id' for user 'api_key'.

    Call handler, then set http status code and return response.

    Args:
        id (int): followed user id
        api_key (str): username who wants to unfollow
        response (Response): fastapi response model for endpoint

    Returns:
        Union[SuccessResponse, ErrorResponse]: success unfollow user or
            error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=} | {id=}")
    error_msg, http_code = await user.unfollow_user(api_key, id)
    project_logger.info(f"{error_msg=}, {http_code=}")
    response.status_code = http_code
    if error_msg:
        return ErrorResponse(**error_msg)
    return SuccessResponse()
