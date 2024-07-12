"""Module with APIRouter for url startswith api/tweets ."""

from typing import Annotated, Union

from fastapi import Header, Response, APIRouter

from app.project_logger import project_logger
from app.services import tweet, tweet_feed
from app.schemas import (
    AddTweetIn,
    AddTweetOut,
    ErrorResponse,
    SuccessResponse,
    TweetFeedOut,
)

router = APIRouter()


@router.post(
    path="/api/tweets",
    description="Add tweet",
    responses={
        201: {"description": "Created", "model": AddTweetOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def add_tweet(
    new_tweet: AddTweetIn,
    api_key: Annotated[str, Header()],
    response: Response,
) -> Union[AddTweetOut, ErrorResponse]:
    """Endpoint for adding new tweet.

    Call handler, then set http status code and return response.

    Args:
        new_tweet (AddTweetIn): tweet details
        api_key (str): author of tweet
        response (Response): fastapi response model for endpoint

    Returns:
        Union[AddTweetOut, ErrorResponse]: success adding tweet or
            error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=} | {new_tweet=}")
    details, http_code = await tweet.add_tweet(api_key, new_tweet)
    project_logger.info(f"{details=}, {http_code=}")
    response.status_code = http_code
    return AddTweetOut(**details)


@router.delete(
    path="/api/tweets/{id}",
    description="Delete tweet by id",
    responses={
        201: {"description": "Created", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def delete_tweet(
    id: int, api_key: Annotated[str, Header()], response: Response,
) -> Union[SuccessResponse, ErrorResponse]:
    """Endpoint for deleting tweet.

    Call handler, then set http status code and return response.

    Args:
        id (int): tweet id
        api_key (str): username who wants to delete tweet
        response (Response): fastapi response model for endpoint

    Returns:
        Union[SuccessResponse, ErrorResponse]: success deleting tweet or
            error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=} | {id=}")
    error_msg, http_code = await tweet.delete_tweet(api_key, id)
    project_logger.info(f"{error_msg=}, {http_code=}")
    response.status_code = http_code
    if error_msg:
        return ErrorResponse(**error_msg)
    return SuccessResponse()


@router.post(
    path="/api/tweets/{id}/likes",
    description="Like tweet by id",
    responses={
        201: {"description": "Created", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def like_tweet_by_id(
    id: int, api_key: Annotated[str, Header()], response: Response,
) -> Union[SuccessResponse, ErrorResponse]:
    """Endpoint to like tweet by its id.

    Call handler, then set http status code and return response.

    Args:
        id (int): tweet id
        api_key (str): username who liking tweet
        response (Response): fastapi response model for endpoint

    Returns:
        Union[SuccessResponse, ErrorResponse]: success like tweet or error
            message with corresponding http status code.

    """
    project_logger.info(f"{api_key=} | {id=}")
    error_msg, http_code = await tweet.like_tweet_by_id(api_key, id)
    project_logger.info(f"{error_msg=}, {http_code=}")
    response.status_code = http_code
    if error_msg:
        return ErrorResponse(**error_msg)
    return SuccessResponse()


@router.delete(
    path="/api/tweets/{id}/likes",
    description="Dislike tweet by id",
    responses={
        201: {"description": "Created", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def dislike_tweet_by_id(
    id: int, api_key: Annotated[str, Header()], response: Response,
) -> Union[SuccessResponse, ErrorResponse]:
    """Endpoint to dislike tweet by its id.

    Call handler, then set http status code and return response.

    Args:
        id (int): tweet id
        api_key (str): username who disliking tweet
        response (Response): fastapi response model for endpoint

    Returns:
        Union[SuccessResponse, ErrorResponse]: success dislike tweet or
            error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=} | {id=}")
    error_msg, http_code = await tweet.dislike_tweet_by_id(api_key, id)
    project_logger.info(f"{error_msg=}, {http_code=}")
    response.status_code = http_code
    if error_msg:
        return ErrorResponse(**error_msg)
    return SuccessResponse()


@router.get(
    path="/api/tweets",
    description="Tweet feed for user",
    responses={
        200: {"description": "OK", "model": TweetFeedOut},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        422: {"description": "Validation Error", "model": ErrorResponse},
    },
)
async def get_tweet_feed(
    api_key: Annotated[str, Header()], response: Response,
) -> Union[TweetFeedOut, ErrorResponse]:
    """Endpoint to get full tweet feed.

    Call handler, then set http status code and return response.

    Args:
        api_key (str): username who request full tweet feed
        response (Response): fastapi response model for endpoint

    Returns:
        Union[TweetFeedOut, ErrorResponse]: success get tweet feeed or
            error message with corresponding http status code.

    """
    project_logger.info(f"{api_key=}")
    # tweet_feed_data, http_code = (
    #     await tweet_feed.get_user_tweet_feed(api_key)
    # )
    tweet_feed_data, http_code = await tweet_feed.get_full_tweet_feed()
    project_logger.info(f"{tweet_feed=}, {http_code=}")
    response.status_code = http_code
    return TweetFeedOut(**tweet_feed_data)
