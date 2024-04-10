from __future__ import annotations
from os import environ as os_environ
from typing import List, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.dialects.postgresql import Insert as PostgresqlInsert
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import (backref, declarative_base, joinedload,
                            mapped_column, Mapped, relationship)
from sqlalchemy import (ARRAY, Column, delete, desc, ForeignKey, func, Insert,
                        Integer, select, Table,  UniqueConstraint)


from project_logger import get_stream_logger

db_logger = get_stream_logger("db_logger")
DATABASE_URL = os_environ.get("DATABASE_URL")
db_logger.info(f"{DATABASE_URL=}")
# DATABASE_URL = "postgresql+asyncpg://admin:admin@127.0.0.1:5432/fake_twitter"
# DATABASE_URL = "postgresql+asyncpg://admin:admin@db:5432/fake_twitter"


def get_async_engine():
    if os_environ.get("PYTEST_ASYNC_ENGINE", None):
        db_logger.info(f"Creating async engine for pytest")
        return create_async_engine(DATABASE_URL, poolclass=NullPool)
    else:
        db_logger.info(f"Creating async engine for production")
        return create_async_engine(DATABASE_URL)


async_engine = get_async_engine()
async_session = async_sessionmaker(bind=async_engine)
Base = declarative_base()

followers = Table(
    "followers",
    Base.metadata,
    Column(
        "follower_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    Column(
        "followed_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    # I follow other user
    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin="User.id == followers.c.follower_id",
        secondaryjoin="User.id == followers.c.followed_id",
        backref=backref("followers", lazy="joined"),
        lazy="joined"
    )

    @classmethod
    async def is_existed_user_name(cls, user_name: str) -> bool:
        db_logger.info(
            f"Checking if {user_name=} is existed in table "
            f"'{cls.__tablename__}'"
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User.id).where(User.name == user_name)
            )
            user_id = user_query.scalar_one_or_none()
            db_logger.info(f"Details of {user_name=}: {user_id=}")
            return True if user_id else False

    @classmethod
    async def get_user_id_by_name(cls, user_name: str) -> int:
        db_logger.info(
            f"Get user id by {user_name=} from table '{cls.__tablename__}'"
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User.id).where(User.name == user_name)
            )
            user_id = user_query.scalar()
            db_logger.info(f"{user_name=}: {user_id=}")
            return user_id

    @classmethod
    async def add_user(cls, user_name: str) -> None:
        db_logger.info(
            f"Add {user_name=} in in table '{cls.__tablename__}'")
        async with async_session() as session:
            async with session.begin():
                session.add(User(name=user_name))

    @classmethod
    async def get_user_by_name(cls, user_name: str) -> Optional[User]:
        db_logger.info(
            f"Get full details of {user_name=} from table "
            f"'{cls.__tablename__}'")
        async with async_session() as session:
            user_query = await session.execute(
                select(User)
                .where(User.name == user_name)
                .options(
                    joinedload(User.followed),
                    joinedload(User.followers),
                )
            )
            user = user_query.unique().scalar_one_or_none()
            db_logger.info(f"Details of {user_name=}: {user}")
            return user

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Optional[User]:
        db_logger.info(
            f"Get full details of {user_id=} from table "
            f"'{cls.__tablename__}'"
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(
                    joinedload(User.followed),
                    joinedload(User.followers),
                )
            )
            user = user_query.unique().scalar_one_or_none()
            db_logger.info(f"Details {user_id=}: {user}")
            return user

    @staticmethod
    async def follow_other_user(follower_id: int, followed_id: int) \
            -> Optional[tuple]:
        db_logger.info(
            f"Add {follower_id=} follow {followed_id=} in table "
            f"'{followers.name}'"
        )
        async with async_session() as session:
            async with session.begin():
                insert_query = (
                    PostgresqlInsert(followers).
                    values(follower_id=follower_id, followed_id=followed_id)
                )
                do_nothing_on_conflict = (
                    insert_query
                    .on_conflict_do_nothing()
                    .returning(followers.c.follower_id,
                               followers.c.followed_id)
                )
                result = await session.execute(do_nothing_on_conflict)
                follow_details = result.one_or_none()
                db_logger.info(f'{follow_details=}')
                return follow_details

    @staticmethod
    async def unfollow_user(follower_id: int, followed_id: int) \
            -> Optional[tuple]:
        db_logger.info(
            f"Delete {follower_id=} follow {followed_id=} in table "
            f"'{followers.name}'"
        )
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(followers)
                    .where(followers.c.follower_id == follower_id,
                           followers.c.followed_id == followed_id)
                    .returning(followers.c.follower_id,
                               followers.c.followed_id)
                )
                delete_details = delete_query.one_or_none()
                db_logger.info(f'{delete_details=}')
                return delete_details


class TweetLike(Base):
    __tablename__ = "tweets_likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tweets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user_name: Mapped[str] = mapped_column(
        ForeignKey(
            "users.name",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user_details = relationship(
        "User",
        primaryjoin="TweetLike.user_name == User.name",
        lazy="joined",
    )
    UniqueConstraint(tweet_id, user_name, name='unique_tweet_like')

    @classmethod
    async def like_tweet(cls, user_name: str, tweet_id: int) -> Optional[int]:
        db_logger.info(f'Like {tweet_id=} by {user_name=}')
        async with async_session() as session:
            async with session.begin():
                insert_query = (
                    PostgresqlInsert(cls)
                    .values(tweet_id=tweet_id,
                            user_name=user_name)
                )
                do_nothing_on_conflict = insert_query.on_conflict_do_nothing(
                    constraint='unique_tweet_like'
                )
                result = await session.execute(
                    do_nothing_on_conflict.returning(cls.id)
                )
                tweet_like_id = result.scalar_one_or_none()
                db_logger.info(f'{tweet_like_id=}')
                return tweet_like_id

    @classmethod
    async def dislike_tweet(cls, user_name: str, tweet_id: int) \
            -> Optional[int]:
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(cls)
                    .where(cls.user_name == user_name,
                           cls.tweet_id == tweet_id)
                    .returning(cls.id)
                )
                tweet_like_id = delete_query.scalar_one_or_none()
                return tweet_like_id


class MediaFile(Base):
    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(nullable=False)
    user_name: Mapped[str] = mapped_column(
        ForeignKey("users.name", ondelete="CASCADE"),
        nullable=False
    )

    @classmethod
    async def add_media_file(cls, user_name: str, file_name: str) -> int:
        db_logger.info(
            f"Adding {file_name=}, {user_name=} in table '{cls.__tablename__}'"
        )
        async with async_session() as session:
            async with session.begin():
                add_query = await session.execute(
                    Insert(cls)
                    .values(user_name=user_name, file_name=file_name)
                    .returning(cls.id)
                )
                media_file_id = add_query.scalar()
                db_logger.info(f"Added {media_file_id=}")
                return media_file_id

    @classmethod
    async def get_media_files_names(cls, ids_list: list) \
            -> list[Optional[str]]:
        db_logger.info(f'Get media file names for {ids_list=}')
        async with async_session() as session:
            select_query = await session.execute(
                select(cls.file_name)
                .where(cls.id.in_(ids_list))
            )
            file_names = select_query.scalars().all()
            db_logger.info(f'{file_names=}')
            return list(file_names)

    @classmethod
    async def bulk_delete(cls, user_name: str, files_ids: list) \
            -> list[Optional[str]]:
        db_logger.info(
            f"Deleting media file {files_ids=} belong to {user_name=} "
            f"from table '{cls.__tablename__}'"
        )
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(cls)
                    .where(cls.user_name == user_name,
                           cls.id.in_(files_ids))
                    .returning(cls.file_name)
                )
                deleted_file_names = delete_query.scalars().all()
            db_logger.info(f'{deleted_file_names=}')
        return list(deleted_file_names)


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(
        ForeignKey("users.name", ondelete="CASCADE"),
        nullable=False
    )
    tweet_data: Mapped[str] = mapped_column(nullable=False)
    tweet_media_ids = Column(ARRAY(Integer))
    author: Mapped[List[User]] = relationship(
        "User",
        primaryjoin="Tweet.author_name == User.name",
        lazy="joined",
    )
    likes: Mapped[List[TweetLike]] = relationship(
        "TweetLike",
        primaryjoin="Tweet.id == TweetLike.tweet_id",
        lazy="joined",
    )

    @classmethod
    async def add_tweet(
            cls,
            author_name: str,
            tweet_data: str,
            tweet_media_ids: list[int] = None) -> int:
        db_logger.info(
            f"Adding {tweet_data=}, {tweet_media_ids=}, {author_name=}"
            f"in table '{cls.__tablename__}'"
        )
        async with async_session() as session:
            async with session.begin():
                add_query = await session.execute(
                    Insert(cls)
                    .values(
                        author_name=author_name,
                        tweet_data=tweet_data,
                        tweet_media_ids=tweet_media_ids)
                    .returning(cls.id)
                )
                tweet_id = add_query.scalar()
            db_logger.info(f"Added {tweet_id=}")
            return tweet_id

    @classmethod
    async def delete_tweet(cls, author_name: str, tweet_id: int) \
            -> Optional[tuple[str, Optional[list[int]]]]:
        db_logger.info(
            f"Deleting {tweet_id=} by {author_name=} from table "
            f"'{cls.__tablename__}'"
        )
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(cls)
                    .where(cls.id == tweet_id,
                           cls.author_name == author_name)
                    .returning(cls.tweet_data,
                               cls.tweet_media_ids)
                )
                deleted_details = delete_query.one_or_none()
                db_logger.info(f"Deleted tweet {deleted_details=}")
                return deleted_details

    @classmethod
    async def get_tweets_by_author_sorted_by_likes(cls, followed_names: list) \
            -> list[Optional[Tweet]]:
        db_logger.info(
            f"Get tweets for {followed_names=} and sort them descending "
            f"by likes from table '{cls.__tablename__}'"
        )
        async with async_session() as session:
            select_query = await session.execute(
                select(cls)
                .where(cls.author_name.in_(followed_names))
                .outerjoin(TweetLike, cls.id == TweetLike.tweet_id)
                .order_by(desc(func.count(TweetLike.id)))
                .group_by(cls.id)
                .options(
                    joinedload(cls.author),
                    joinedload(cls.likes)
                    .options(joinedload(TweetLike.user_details)
                             )
                )
            )
            user_tweets = select_query.unique().scalars().all()
            db_logger.info(f"{user_tweets=}")
        return list(user_tweets)

    @classmethod
    async def get_all_tweets_sorted_by_likes(cls) -> list[Optional[Tweet]]:
        db_logger.info(
            f"Get all tweets sorted descending by likes"
            f" from table '{cls.__tablename__}'"
        )
        async with async_session() as session:
            select_query = await session.execute(
                select(cls)
                .outerjoin(TweetLike, cls.id == TweetLike.tweet_id)
                .order_by(desc(func.count(TweetLike.id)))
                .group_by(cls.id)
                .options(
                    joinedload(cls.author),
                    joinedload(cls.likes)
                    .options(joinedload(TweetLike.user_details)
                             )
                )
            )
            all_tweets = select_query.unique().scalars().all()
            db_logger.info(f"{all_tweets=}")
        return list(all_tweets)


async def create_tables() -> None:
    """Create tables in db"""

    async with async_engine.begin() as conn:
        db_logger.info("Dropping all table in db")
        await conn.run_sync(Base.metadata.drop_all)

        db_logger.info("Creating tables which are not existed in db.")
        await conn.run_sync(Base.metadata.create_all)

        db_logger.info("Completed creating tables in db.")


async def init_db() -> None:
    """
    Create tables and insert data in table 'users' if User.name == test is not
    existed.
    """

    db_logger.info("initializing db")
    await create_tables()
    if not await User.is_existed_user_name("test"):
        db_logger.info("Adding default data in db")
        async with async_session() as session:
            test = User(name='test')
            alex = User(name='Alex')
            petr = User(name='Petr')
            amigo = User(name='Amigo')
            nikole = User(name='Nikole')
            alex.followed.append(petr)
            alex.followed.append(amigo)
            alex.followers.append(nikole)
            alex.followers.append(amigo)
            amigo.followed.append(petr)
            nikole.followed.append(amigo)
            nikole.followed.append(petr)
            media_file_1 = MediaFile(
                file_name='champions_1.png', user_name='Alex'
            )
            media_file_2 = MediaFile(
                file_name='champions_2.png', user_name='Alex'
            )
            media_file_3 = MediaFile(
                file_name='good_morning.jpg', user_name='Alex'
            )
            media_file_4 = MediaFile(
                file_name='sun_rise.jpg', user_name='Petr'
            )
            media_file_5 = MediaFile(
                file_name='vacation.jpg', user_name='Nikole'
            )
            tweet_1 = Tweet(
                author_name='Alex',
                tweet_data='!!!Hala Madrid!!!',
                tweet_media_ids=[1, 2]
            )
            tweet_2 = Tweet(
                author_name='Alex',
                tweet_data='Good morning=))',
                tweet_media_ids=[3]
            )
            tweet_3 = Tweet(
                author_name='Petr',
                tweet_data='Today is a nice day!',
                tweet_media_ids=[4]
            )
            tweet_4 = Tweet(
                author_name='Nikole',
                tweet_data='Awaited vacation after hard working year...',
                tweet_media_ids=[5]
            )
            tweet_5 = Tweet(
                author_name='Nikole',
                tweet_data='Again raining)',
            )
            like_1_1 = TweetLike(tweet_id=1, user_name='Nikole')
            like_2_1 = TweetLike(tweet_id=2, user_name='Nikole')
            like_2_2 = TweetLike(tweet_id=2, user_name='Amigo')
            like_3_1 = TweetLike(tweet_id=3, user_name='Nikole')
            like_3_2 = TweetLike(tweet_id=3, user_name='Amigo')
            like_3_3 = TweetLike(tweet_id=3, user_name='Alex')
            like_4_1 = TweetLike(tweet_id=4, user_name='Nikole')
            like_4_2 = TweetLike(tweet_id=4, user_name='Alex')
            session.add_all(
                [
                    test,
                    alex,
                    petr,
                    amigo,
                    nikole
                ]
            )
            await session.commit()
            session.add_all(
                [
                    media_file_1,
                    media_file_2,
                    media_file_3,
                    media_file_4,
                    media_file_5,
                    tweet_1,
                    tweet_2,
                    tweet_3,
                    tweet_4,
                    tweet_5
                ]
            )
            await session.commit()
            session.add_all(
                [
                    like_1_1,
                    like_2_1,
                    like_2_2,
                    like_3_1,
                    like_3_2,
                    like_3_3,
                    like_4_1,
                    like_4_2
                ]
            )
            await session.commit()


async def close_db_connection() -> None:
    """Dispose connection with db"""

    db_logger.info("Disposing async engine")
    await async_engine.dispose()
