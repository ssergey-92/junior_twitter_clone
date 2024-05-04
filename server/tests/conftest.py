from os import (
    environ as os_environ,
    listdir as os_listdir,
    mkdir as os_mkdir,
    path as os_path
)
from shutil import rmtree as shutil_rmtree, copy as shutil_copy

from aiofiles import os as aio_os
from fastapi import FastAPI
from pytest import fixture as sync_fixture
from pytest_asyncio import fixture as async_fixture
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.database import (async_engine, async_session, Base, MediaFile,
                                 Tweet,
                                 TweetLike, User)
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
    test_user_1,
    test_user_2,
    test_user_3,
    TWEET_1,
    TWEET_2,
    TWEET_3
)
from server.app.routes import get_fake_twitter_app, application


# async def override_dependency_save_media_file_in_sys(
#             media_file: UploadFile,
#             unique_filename: str) -> None:
#     # 'app/tests/test_images'
#     pass
#
# application.dependency_overrides[HandleEndpoint._save_media_file_in_sys] \
#         = override_dependency_save_media_file_in_sys


@async_fixture(scope="session")
async def app() -> FastAPI:
    print('0000000000000000000000000000', 'creating app')
    os_environ["SAVE_MEDIA_PATH"] = SAVE_MEDIA_ABS_PATH
    # application = await get_fake_twitter_app()
    return application


@sync_fixture(scope="session")
async def app_routes(app) -> list:
    print('000000000000000011111111', 'creating app.routes')
    return [route.path for route in app.routes]


# @sync_fixture(autouse=True, scope="session")
# def app() -> FastAPI:
#     application = fake_twitter_app
#     yield application
#
#
# @sync_fixture(autouse=True, scope="session")
# def api_routes_details(app) -> list:
#     api_routes = list()
#     for route in app.routes:
#         if route.path.startswith('/api/'):
#             api_routes.append((route.path, route.methods))
#     yield api_routes


@async_fixture(autouse=True, scope="session")
async def client(app) -> AsyncClient:
    print(1111111111111111111111111111111111, 'client')
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test") as async_client:
        yield async_client


@async_fixture(scope="function")
async def test_session() -> AsyncSession:
    print(22222222222222222222222222222222222222222, 'session')
    async with async_session() as session:
        yield session


@async_fixture(scope="function")
async def recreate_all_tables() -> None:
    print(333333333333333333333333333, 'recriate')
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@async_fixture(autouse=True, scope="function")
async def init_test_data_for_db(recreate_all_tables: None,
                                test_session: AsyncSession) -> None:
    print(444444444444444444444444444444444, 'init data')
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
                user_name=MEDIA_FILE_1["user_name"]
            ),
            MediaFile(
                file_name=MEDIA_FILE_2["file_name"],
                user_name=MEDIA_FILE_2["user_name"]
            ),
            MediaFile(
                file_name=MEDIA_FILE_3["file_name"],
                user_name=MEDIA_FILE_3["user_name"]
            ),
            Tweet(
                author_name=TWEET_1["author_name"],
                tweet_data=TWEET_1["tweet_data"],
                tweet_media_ids=TWEET_1.get("tweet_media_ids", None)
            ),
            Tweet(
                author_name=TWEET_2["author_name"],
                tweet_data=TWEET_2["tweet_data"],
                tweet_media_ids=TWEET_2.get("tweet_media_ids", None)
            ),
            Tweet(
                author_name=TWEET_3["author_name"],
                tweet_data=TWEET_3["tweet_data"],
                tweet_media_ids=TWEET_3.get("tweet_media_ids", None)
            )
        ]
    )
    await test_session.commit()
    test_session.add_all(
        [
            TweetLike(
                tweet_id=LIKE_1_1["tweet_id"], user_name=LIKE_1_1["user_name"]
            ),
            TweetLike(
                tweet_id=LIKE_2_2["tweet_id"], user_name=LIKE_2_2["user_name"]
            ),
            TweetLike(
                tweet_id=LIKE_2_3["tweet_id"], user_name=LIKE_2_3["user_name"]
            ),
            TweetLike(
                tweet_id=LIKE_3_1["tweet_id"], user_name=LIKE_3_1["user_name"]
            ),
            TweetLike(
                tweet_id=LIKE_3_2["tweet_id"], user_name=LIKE_3_2["user_name"]
            ),
            TweetLike(
                tweet_id=LIKE_3_3["tweet_id"], user_name=LIKE_3_3["user_name"]
            )
        ]
    )
    await test_session.commit()


@sync_fixture(scope="function")
def init_test_folders() -> None:
    if os_path.exists(SAVE_MEDIA_ABS_PATH):
        print(66666666666666666666666666666666, 'delete_media_files_from_test')
        shutil_rmtree(SAVE_MEDIA_ABS_PATH)

    print(44444444444444444555555555555555555, ' init_test_folders')
    os_mkdir(SAVE_MEDIA_ABS_PATH)
    yield
    print(66666666666666666666666666666666, 'delete_media_files_from_test')
    shutil_rmtree(SAVE_MEDIA_ABS_PATH)


@sync_fixture(scope="function")
def init_midia_file_for_test(init_test_folders) -> None:
    print(55555555555555555555555555, 'handle_saving_images_during_test')
    print(SAVE_MEDIA_ABS_PATH)

    for i_filename in os_listdir(DEFAULT_TEST_IMAGES_PATH):
        shutil_copy(
            os_path.join(DEFAULT_TEST_IMAGES_PATH, i_filename),
            os_path.join(SAVE_MEDIA_ABS_PATH, i_filename)
        )
