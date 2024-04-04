from contextlib import asynccontextmanager
from typing import Annotated, Any, Union

from fastapi import FastAPI, Form, Header, UploadFile, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request as StarletteRequest

from database import init_db, close_db_connection
from models import HandleEndpoint
from my_logger import get_stream_logger
from schemas import (
    AddTweetIn,
    AddTweetOut,
    AddMediaOut,
    SuccessResponse,
    TweetFeedOut,
    UserProfileDetailsOut,
    ErrorResponse,
)

routes_logger = get_stream_logger("routes_logger")


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    Initialize db with tables if there are not existed before starting
    fast api application 'app' and close db connection after stopping it

    :param app: FastApi application
    :type app:FastAPI
    """

    routes_logger.info("Started lifespan")
    await init_db()
    yield
    await close_db_connection()


app = FastAPI(title="fake_twitter", lifespan=lifespan)


# def get_fast_api_app() -> FastAPI:
#     app = FastAPI()
#     return app


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
        request: StarletteRequest,
        exc: StarletteHTTPException) -> JSONResponse:
    routes_logger.info(f"Caught exception: {exc}")
    return JSONResponse(
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "HTTPException",
                "error_message": exc.detail,
            }
        ),
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: StarletteRequest,
        exc: RequestValidationError) -> JSONResponse:
    routes_logger.info(f"Caught exception: {exc}")
    return JSONResponse(
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "Bad Request",
                "error_message": exc.errors(),
            }
        ),
        status_code=400
    )


@app.post(
    path="/api/tweets",
    description="Add tweet",
    responses={
        201: {"description": "Created", "model": AddTweetOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    },
)
async def add_tweet(
        new_tweet: AddTweetIn,
        api_key: Annotated[str, Header()],
        response: Response
) -> Union[AddTweetOut, ErrorResponse]:
    routes_logger.info(f"{api_key=} | {new_tweet=}")
    data, http_code = await HandleEndpoint.add_tweet(api_key, new_tweet)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return AddTweetOut(**data)
    else:
        return ErrorResponse(**data)


@app.post(
    path="/api/medias",
    description="Add media file",
    responses={
        201: {"description": "Created", "model": AddMediaOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def add_media_file(
        file: Annotated[UploadFile, Form()],
        api_key: Annotated[str, Header()],
        response: Response) -> Union[AddMediaOut, ErrorResponse]:
    # change type to str

    routes_logger.info(f"{api_key=}, {file=}")

    data, http_code = await HandleEndpoint.add_media_file(
        api_key,
        file
    )
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return AddMediaOut(**data)
    else:
        return ErrorResponse(**data)

    # return {"media_id": 1}


@app.delete(
    path="/api/tweets/{id}",
    description="Delete tweet by id",
    responses={
        200: {"description": "OK", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def delete_tweet(
        id: int,
        api_key: Annotated[str, Header()],
        response: Response) -> Union[SuccessResponse, ErrorResponse]:
    routes_logger.info(f"{api_key=} | {id=}")
    data, http_code = await HandleEndpoint.delete_tweet(api_key, id)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 200:
        return SuccessResponse()
    else:
        return ErrorResponse(**data)


@app.post(
    path="/api/tweets/{id}/likes",
    description="Like tweet by id",
    responses={
        201: {"description": "OK", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def like_tweet_by_id(
        id: int,
        api_key: Annotated[str, Header()],
        response: Response) -> Union[SuccessResponse, ErrorResponse]:
    routes_logger.info(f"{api_key=} | {id=}")
    data, http_code = await HandleEndpoint.like_tweet_by_id(api_key, id)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return SuccessResponse()
    else:
        return ErrorResponse(**data)


@app.delete(
    path="/api/tweets/{id}/likes",
    description="Dislike tweet by id",
    responses={
        201: {"description": "OK", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def dislike_tweet_by_id(
        id: int,
        api_key: Annotated[str, Header()],
        response: Response) -> Union[SuccessResponse, ErrorResponse]:
    routes_logger.info(f"{api_key=} | {id=}")
    data, http_code = await HandleEndpoint.dislike_tweet_by_id(api_key, id)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return SuccessResponse()
    else:
        return ErrorResponse(**data)

    # return {}


@app.post(
    path="/api/users/{id}/follow",
    description="Follow user by id",
    responses={
        201: {"description": "OK", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def follow_other_user(
        id: int,
        api_key: Annotated[str, Header()],
        response: Response) -> Union[SuccessResponse, ErrorResponse]:
    routes_logger.info(f"{api_key=} | {id=}")
    data, http_code = await HandleEndpoint.follow_other_user(api_key, id)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return SuccessResponse()
    else:
        return ErrorResponse(**data)

    # return {}


@app.delete(
    path="/api/users/{id}/follow",
    description="Unsubscribe from user by id",
    responses={
        201: {"description": "OK", "model": SuccessResponse},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def unfollow_user(
        id: int,
        api_key: Annotated[str, Header()],
        response: Response) -> Union[SuccessResponse, ErrorResponse]:
    routes_logger.info(f"{api_key=} | {id=}")
    data, http_code = await HandleEndpoint.unfollow_user(api_key, id)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 201:
        return SuccessResponse()
    else:
        return ErrorResponse(**data)


@app.get(
    path="/api/tweets",
    description="Tweet feed for user",
    responses={
        200: {"description": "OK", "model": TweetFeedOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def get_tweet_feed(
        api_key: Annotated[str, Header()],
        response: Response) -> Union[TweetFeedOut, ErrorResponse]:
    routes_logger.info(f"{api_key=}")

    # data, http_code = await HandleEndpoint.get_user_tweet_feed(api_key)
    data, http_code = await HandleEndpoint.get_full_tweet_feed(api_key)

    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 200:
        return TweetFeedOut(**data)
    else:
        return ErrorResponse(**data)

    # return {
    #     "tweets": [
    #         {
    #             "id": 1,
    #             "content": "some content for tweet feed ",
    #             "attachments": ["link_1"],
    #             "author": {
    #                 "id": 1,
    #                 "name": "Sergey_1",
    #             },
    #             "likes": [
    #                 {
    #                     "user_id": 2,
    #                     "name": "Alex",
    #                 }
    #             ],
    #         }
    #     ]
    # }


@app.get(
    path="/api/users/me",
    description="User own profile details",
    responses={
        200: {"description": "OK", "model": UserProfileDetailsOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def get_own_profile_details(
        api_key: Annotated[str, Header()],
        response: Response) -> Union[UserProfileDetailsOut, ErrorResponse]:
    routes_logger.info(f"{api_key=}")
    data, http_code = await HandleEndpoint.get_own_profile_details(api_key)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 200:
        return UserProfileDetailsOut(**data)
    else:
        return ErrorResponse(**data)


@app.get(
    path="/api/users/{id}",
    description="Get user profile details by id",
    responses={
        200: {"description": "OK", "model": UserProfileDetailsOut},
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse}
    }
)
async def get_user_profile_details(
        id: int,
        api_key: Annotated[str, Header()],
        response: Response) -> Union[UserProfileDetailsOut, ErrorResponse]:
    routes_logger.info(f"{api_key=}")
    data, http_code = await HandleEndpoint.get_user_profile_details(api_key,
                                                                    id)
    routes_logger.info(f"{data=}, {http_code=}")
    response.status_code = http_code
    if http_code == 200:
        return UserProfileDetailsOut(**data)
    else:
        return ErrorResponse(**data)

    # get_user_profile_details
    # return {
    #     "user": {
    #         "id": 2,
    #         "name": 'other_user',
    #         "followers": [
    #             {
    #                 "id": 3,
    #                 "name": "follower 3"
    #             }
    #         ],
    #         "following": [
    #             {
    #                 "id": 4,
    #                 "name": "following 4"
    #             }
    #         ]
    #     }
    # }

    # get_own_profile_details
    # return {
    #     "user": {
    #         "id": 1,
    #         "name": api_key,
    #         "followers": [{"id": 0, "name": "follower 1"}],
    #         "following": [{"id": 2, "name": "following 1"}],
    #     }
    # }
