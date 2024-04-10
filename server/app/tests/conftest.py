from fastapi import FastAPI
from pytest_asyncio import fixture as async_fixture
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..routes import application as fake_twitter_app
from ..database import (async_engine, async_session, Base, MediaFile, Tweet,
                        TweetLike, User)


@async_fixture(autouse=True, scope="session")
async def app() -> FastAPI:
    application = fake_twitter_app
    yield application


@async_fixture(autouse=True, scope="session")
async def app_routes(app) -> list:
    yield [route.path for route in app.routes]


@async_fixture(autouse=True, scope="function")
async def client(app) -> AsyncClient:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test") as ac:
        yield ac


@async_fixture(autouse=True, scope="function")
async def test_session() -> async_sessionmaker:
    async with async_session() as session:
        yield session


@async_fixture(autouse=True, scope="function")
async def recreate_all_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@async_fixture(autouse=True, scope="function")
async def init_test_data(recreate_all_tables, test_session) -> None:
    test_1 = User(name='test_1')
    test_2 = User(name='test_2')
    test_3 = User(name='test_3')
    test_1.followed.append(test_2)
    test_1.followers.append(test_3)
    media_file_1 = MediaFile(file_name='test_1.png', user_name='test_1')
    media_file_2 = MediaFile(file_name='test_2.png', user_name='test_2')
    media_file_3 = MediaFile(file_name='test_22.png', user_name='test_2')
    tweet_1 = Tweet(
        author_name='test_1',
        tweet_data='tweet of test_1 user',
        tweet_media_ids=[1]
    )
    tweet_2 = Tweet(
        author_name='test_2',
        tweet_data='tweet of test_2 user',
        tweet_media_ids=[2, 3]
    )
    tweet_3 = Tweet(author_name='test_3', tweet_data='tweet of test_3 user')
    like_1_1 = TweetLike(tweet_id=1, user_name='test_1')
    like_2_2 = TweetLike(tweet_id=2, user_name='test_2')
    like_2_3 = TweetLike(tweet_id=2, user_name='test_3')
    like_3_1 = TweetLike(tweet_id=3, user_name='test_1')
    like_3_2 = TweetLike(tweet_id=3, user_name='test_2')
    like_3_3 = TweetLike(tweet_id=3, user_name='test_3')
    test_session.add_all([test_1, test_2, test_3])
    await test_session.commit()
    test_session.add_all(
        [
            media_file_1,
            media_file_2,
            media_file_3,
            tweet_1,
            tweet_2,
            tweet_3,
        ]
    )
    await test_session.commit()
    test_session.add_all(
        [
            like_1_1,
            like_2_2,
            like_2_3,
            like_3_1,
            like_3_2,
            like_3_3,
        ]
    )
    await test_session.commit()
