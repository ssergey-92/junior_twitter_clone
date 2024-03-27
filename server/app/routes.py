


from typing import Annotated, Any
from fastapi import FastAPI, Header, Form

from my_logger import get_stream_logger
from schemas import AddTweetIn, AddTweetOut, MediaOut, SuccessResponse, \
    TweetFeedOut, UserProfileDetailsOut

app = FastAPI()
routes_logger = get_stream_logger('routes')


def get_fast_api_app() -> FastAPI:
    app = FastAPI()
    return app


@app.post(
    path='/api/tweets',
    description='Add tweet',
    response_model=AddTweetOut)
async def add_tweet(
        tweet: AddTweetIn,
        api_key: Annotated[str, Header()]):

    routes_logger.info(f'{api_key=} | {tweet=}')
    return {"tweet_id": 1}


@app.post(
    path='/api/medias',
    description='Add media file',
    response_model=MediaOut
)
async def add_media(
        file: Annotated[Any, Form()],
        api_key: Annotated[str, Header()]):
    # change type to str

    routes_logger.info(f'{api_key=} | {type(file)=} | {file=}')
    return {"media_id": 1}


@app.delete(
    path='/api/tweets/{id}',
    description='Delete tweet by id',
    response_model=SuccessResponse
)
async def delete_tweet(
        id: int,
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=} | {id=}')
    return {}


@app.post(
    path='/api/tweets/{id}/likes',
    description='Like tweet by id',
    response_model=SuccessResponse
)
async def like_tweet_by_id(
        id: int,
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=} | {id=}')
    return {}


@app.delete(
    path='/api/tweets/{id}/likes',
    description='Dislike tweet by id',
    response_model=SuccessResponse
)
async def dislike_tweet_by_id(
        id: int,
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=} | {id=}')
    return {}


@app.post(
    path='/api/users/{id}/follow',
    description='Follow user by id',
    response_model=SuccessResponse
)
async def follow_user_by_id(
        id: int,
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=} | {id=}')
    return {}


@app.delete(
    path='/api/users/{id}/follow',
    description='Unsubscribe from user by id',
    response_model=SuccessResponse
)
async def unsubscribe_from_user_by_id(
        id: int,
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=} | {id=}')
    return {}


@app.get(
    path='/api/tweets',
    description='Tweet feed for user',
    response_model=TweetFeedOut
)
async def user_tweet_feed(
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=}')
    return {
        "tweets": [
            {
                "id": 1,
                "content": "some content for tweet feed ",
                "attachments": [
                    "link_1"
                ],
                "author": {
                    "id": 1,
                    "name": "Sergey_1"
                },
                "likes": [
                    {
                        "user_id": 2,
                        "name": "Alex"
                    }
                ]
            }
        ]
    }


@app.get(
    path='/api/users/me',
    description='User profile details',
    response_model=UserProfileDetailsOut
)
async def user_profile_details(
        api_key: Annotated[str, Header()]) -> dict:

    routes_logger.info(f'{api_key=}')
    return {
        "user": {
            "id": 1,
            "name": api_key,
            "followers": [
                {
                    "id": 0,
                    "name": "follower 1"
                }
            ],
            "following": [
                {
                    "id": 2,
                    "name": "following 1"
                }
            ]
        }
    }