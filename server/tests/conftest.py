"""Configuration file for pytest."""
from os import environ as os_environ
from os import listdir as os_listdir
from os import mkdir as os_mkdir
from os import path as os_path
from shutil import copy as shutil_copy
from shutil import rmtree as shutil_rmtree

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pytest import fixture as sync_fixture
from pytest_asyncio import fixture as async_fixture
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import AsyncGenerator

from server.app.database import (
    Base,
    MediaFile,
    Tweet,
    TweetLike,
    User,
    async_engine,
    async_session,
)
from server.app.routes import application
from .common_data_for_tests import (
    DEFAULT_TEST_IMAGES_PATH,
    LIKE_1_1,
    LIKE_2_2,
    LIKE_2_3,
    LIKE_3_1,
    LIKE_3_2,
    LIKE_3_3,
    MEDIA_FILE_1,
    MEDIA_FILE_2,
    MEDIA_FILE_3,
    SAVE_MEDIA_ABS_PATH,
    TWEET_1,
    TWEET_2,
    TWEET_3,
    test_user_1,
    test_user_2,
    test_user_3,
)


@async_fixture(autouse=True, scope="session")
async def add_paths_to_os_environ() -> None:
    """Add 'SAVE_MEDIA_PATH' to os.environ."""
    os_environ["SAVE_MEDIA_PATH"] = SAVE_MEDIA_ABS_PATH


@async_fixture(scope="function")
async def reset_os_environ_paths() -> AsyncGenerator:
    """Add 'SAVE_MEDIA_PATH' to os.environ. after func call."""
    yield
    os_environ["SAVE_MEDIA_PATH"] = SAVE_MEDIA_ABS_PATH


@async_fixture(scope="session")
async def app() -> FastAPI:
    """Return FastApi app."""
    return application


@sync_fixture(scope="session")
async def app_routes(app) -> list:
    """Return list of urls for of application."""
    return [route.path for route in app.routes]


@async_fixture(scope="session")
async def client(app) -> AsyncClient:
    """Yield asynchronous client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test",
    ) as async_client:
        yield async_client


@async_fixture(scope="function")
async def test_session() -> AsyncSession:
    """Yield asynchronous session for db connection."""
    async with async_session() as session:
        yield session


@async_fixture(scope="function")
async def recreate_all_tables() -> None:
    """Remove and then create all tables for db."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@async_fixture(scope="function")
async def init_test_data_for_db(
    recreate_all_tables: None, test_session: AsyncSession,
) -> None:
    """Init db default test data for testing."""
    test_1 = User(name=test_user_1["name"])
    test_2 = User(name=test_user_2["name"])
    test_3 = User(name=test_user_3["name"])
    test_1.followed.append(test_2)
    test_1.followers.append(test_3)
    test_session.add_all([test_1, test_2, test_3])
    await test_session.commit()
    test_session.add_all(
        [
            MediaFile(
                file_name=MEDIA_FILE_1["file_name"],
                user_name=MEDIA_FILE_1["user_name"],
            ),
            MediaFile(
                file_name=MEDIA_FILE_2["file_name"],
                user_name=MEDIA_FILE_2["user_name"],
            ),
            MediaFile(
                file_name=MEDIA_FILE_3["file_name"],
                user_name=MEDIA_FILE_3["user_name"],
            ),
            Tweet(
                author_name=TWEET_1["author_name"],
                tweet_data=TWEET_1["tweet_data"],
                tweet_media_ids=TWEET_1.get("tweet_media_ids", None),
            ),
            Tweet(
                author_name=TWEET_2["author_name"],
                tweet_data=TWEET_2["tweet_data"],
                tweet_media_ids=TWEET_2.get("tweet_media_ids", None),
            ),
            Tweet(
                author_name=TWEET_3["author_name"],
                tweet_data=TWEET_3["tweet_data"],
                tweet_media_ids=TWEET_3.get("tweet_media_ids", None),
            ),
        ],
    )
    await test_session.commit()
    test_session.add_all(
        [
            TweetLike(
                tweet_id=LIKE_1_1["tweet_id"], user_name=LIKE_1_1["user_name"],
            ),
            TweetLike(
                tweet_id=LIKE_2_2["tweet_id"], user_name=LIKE_2_2["user_name"],
            ),
            TweetLike(
                tweet_id=LIKE_2_3["tweet_id"], user_name=LIKE_2_3["user_name"],
            ),
            TweetLike(
                tweet_id=LIKE_3_1["tweet_id"], user_name=LIKE_3_1["user_name"],
            ),
            TweetLike(
                tweet_id=LIKE_3_2["tweet_id"], user_name=LIKE_3_2["user_name"],
            ),
            TweetLike(
                tweet_id=LIKE_3_3["tweet_id"], user_name=LIKE_3_3["user_name"],
            ),
        ],
    )
    await test_session.commit()


@sync_fixture(scope="function")
def init_test_folders() -> AsyncGenerator:
    """create test folders for saving media and remove then after test."""
    if os_path.exists(SAVE_MEDIA_ABS_PATH):
        shutil_rmtree(SAVE_MEDIA_ABS_PATH)
    os_mkdir(SAVE_MEDIA_ABS_PATH)
    yield
    shutil_rmtree(SAVE_MEDIA_ABS_PATH)


@sync_fixture(scope="function")
def init_midia_file_for_test(init_test_folders) -> None:
    """Init media files for test."""
    for i_filename in os_listdir(DEFAULT_TEST_IMAGES_PATH):
        shutil_copy(
            os_path.join(DEFAULT_TEST_IMAGES_PATH, i_filename),
            os_path.join(SAVE_MEDIA_ABS_PATH, i_filename),
        )
