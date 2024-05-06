from os import environ as os_environ

from pytest import mark as pytest_mark
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from ..app.database import (
    MediaFile,
    Tweet,
    TweetLike,
    User,
    followers,
    get_async_engine,
    init_db,
)
from .common_data_for_tests import DEFAULT_TABLE_NAMES


def test_get_async_engine():
    async_engine = get_async_engine()
    assert async_engine.pool.status() == "NullPool"
    os_environ.pop("PYTEST_ASYNC_ENGINE")
    async_engine = get_async_engine()
    assert async_engine.pool.status() != "NullPool"


@pytest_mark.asyncio
async def test_create_tables(test_session: AsyncSession):
    table_names_query = await test_session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    )
    table_names = table_names_query.scalars().fetchall()
    assert table_names == DEFAULT_TABLE_NAMES


@pytest_mark.asyncio
async def test_init_db(recreate_all_tables, test_session: AsyncSession):
    await init_db()
    total_users = await test_session.execute(select(func.count(User.id)))
    assert total_users.scalar() == 5
    total_media_files = await test_session.execute(
        select(func.count(MediaFile.id))
    )
    assert total_media_files.scalar() == 5
    total_tweets = await test_session.execute(select(func.count(Tweet.id)))
    assert total_tweets.scalar() == 5
    total_likes = await test_session.execute(select(func.count(TweetLike.id)))
    assert total_likes.scalar() == 8
    total_followers = await test_session.execute(
        select(func.count(followers.c.follower_id))
    )
    assert total_followers.scalar() == 7
