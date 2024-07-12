"""Module for testing db initialization and connection functions ."""

from os import environ as os_environ

from pytest import mark as pytest_mark, raises as pytest_raises
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from .common import DEFAULT_TABLE_NAMES
from app.models.connection import get_async_engine
from app.models.initialization import init_db
from app.models.media_files import MediaFile
from app.models.tweets import Tweet
from app.models.tweet_likes import TweetLike
from app.models.users import User, followers


def test_get_async_engine() -> None:
    async_engine = get_async_engine()
    assert async_engine.pool.status() == "NullPool"
    os_environ.pop("PYTEST_ASYNC_ENGINE")
    async_engine = get_async_engine()
    assert async_engine.pool.status() != "NullPool"
    os_environ.pop("DATABASE_URL")
    with pytest_raises(SystemExit):
        get_async_engine()


@pytest_mark.asyncio
async def test_create_tables(
    test_session: AsyncSession,
) -> None:
    table_names_query = await test_session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"),
    )
    table_names = table_names_query.scalars().fetchall()
    sorted_table_names = sorted(table_names)
    assert sorted_table_names == DEFAULT_TABLE_NAMES


@pytest_mark.asyncio
async def test_init_db(
    clear_test_db_tables: None, test_session: AsyncSession,
) -> None:
    await init_db()
    total_users = await test_session.execute(select(func.count(User.id)))
    assert total_users.scalar() == 5
    total_media_files = await test_session.execute(
        select(func.count(MediaFile.id)),
    )
    assert total_media_files.scalar() == 5
    total_tweets = await test_session.execute(select(func.count(Tweet.id)))
    assert total_tweets.scalar() == 5
    total_likes = await test_session.execute(select(func.count(TweetLike.id)))
    assert total_likes.scalar() == 8
    total_followers = await test_session.execute(
        select(func.count(followers.c.follower_id)),
    )
    assert total_followers.scalar() == 7
