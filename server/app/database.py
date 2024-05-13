"""Module for working with project PostgreSQL database."""

from __future__ import annotations

from os import environ as os_environ
from sys import exit as sys_exit
from typing import Optional, Union

from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Integer,
    Table,
    UniqueConstraint,
    delete,
    desc,
    func,
    insert,
    select,
)
from sqlalchemy.dialects.postgresql import Insert as PostgresqlInsert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Mapped,
    backref,
    declarative_base,
    joinedload,
    mapped_column,
    relationship,
)
from sqlalchemy.pool import NullPool

from project_logger import fake_twitter_logger

os_environ["DATABASE_URL"] = "postgresql+asyncpg://admin:admin@db:5432/fake_twitter"
def get_async_engine() -> AsyncEngine:
    """Get asynchronous engine.

    If 'DATABASE_URL' is not set in os environ, call system exit. Then if
    'PYTEST_ASYNC_ENGINE' is set in os environ return asynchronous engine with
    set poolclass=NullPool else without setting poolclass.

    Returns:
        AsyncEngine : asynchronous engine

    """
    db_url = os_environ.get("DATABASE_URL", None)
    fake_twitter_logger.info(f"{db_url=}")
    if db_url:
        if os_environ.get("PYTEST_ASYNC_ENGINE", None):
            fake_twitter_logger.info("Creating async engine for pytest")
            return create_async_engine(db_url, poolclass=NullPool)
        fake_twitter_logger.info("Creating async engine for production")
        return create_async_engine(db_url)
    sys_exit("DATABASE_URL should be set to run the program!")


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
        primary_key=True,
    ),
    Column(
        "followed_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    """ORM Mapped Class User, parent class Base.

    Class for creating and dealing with table 'users'.

    Attributes:
        id (Optional[int]): user id, unique identifier of user
        name (str): username
        followed (list[Optional[User]]): followed users

    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    followed = relationship(
        "User",
        secondary=followers,
        primaryjoin="User.id == followers.c.follower_id",
        secondaryjoin="User.id == followers.c.followed_id",
        backref=backref("followers", lazy="joined"),
        lazy="joined",
    )

    @classmethod
    async def is_existed_user_name(cls, user_name: str) -> bool:
        """Check if username is existed.

        Args:
            user_name (str): username

        Returns:
            bool : True if user is existed else False

        """
        fake_twitter_logger.info(
            f"Checking if {user_name=} is existed in table "
            f"'{cls.__tablename__}'",
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User.id).where(User.name == user_name),
            )
            user_id = user_query.scalar_one_or_none()
        fake_twitter_logger.info(f"Details of {user_name=}: {user_id=}")
        return user_id is not None

    @classmethod
    async def get_user_id_by_name(cls, user_name: str) -> Optional[int]:
        """Get user id by username.

        Returns user id if user_name is existed.

        Args:
            user_name (str): username

        Returns:
            Optional[int] : user id

        """
        fake_twitter_logger.info(
            f"Get user id by {user_name=} from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User.id).where(User.name == user_name),
            )
            user_id = user_query.scalar_one_or_none()
        fake_twitter_logger.info(f"{user_name=}: {user_id=}")
        return user_id

    @classmethod
    async def add_user(cls, user_name: str) -> None:
        """Add new user.

        Args:
            user_name (str): username

        """
        fake_twitter_logger.info(
            f"Add {user_name=} in in table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            async with session.begin():
                session.add(User(name=user_name))

    @classmethod
    async def get_user_by_name(cls, user_name: str) -> Optional[User]:
        """Get User by username.

        Returns User if user_name is existed.

        Args:
            user_name (str): username

        Returns:
            Optional[User] : user

        """
        fake_twitter_logger.info(
            f"Get full details of {user_name=} from table "
            f"'{cls.__tablename__}'",
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User).
                where(User.name == user_name).
                options(
                    joinedload(User.followed),
                    joinedload(User.followers),
                ),
            )
            user = user_query.unique().scalar_one_or_none()
        fake_twitter_logger.info(f"Details of {user_name=}: {user}")
        return user

    @classmethod
    async def get_user_by_id(cls, user_id: int) -> Optional[User]:
        """Get User by user id.

        Returns User if user_id is existed.

        Args:
            user_id (int): user id

        Returns:
            Optional[User] : user

        """
        fake_twitter_logger.info(
            f"Get full details of {user_id=} from table "
            f"'{cls.__tablename__}'",
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User).
                where(User.id == user_id).
                options(
                    joinedload(User.followed),
                    joinedload(User.followers),
                ),
            )
            user = user_query.unique().scalar_one_or_none()
        fake_twitter_logger.info(f"Details {user_id=}: {user}")
        return user

    @staticmethod
    async def follow_other_user(
        follower_id: int, followed_id: int,
    ) -> Optional[Row]:
        """Add followed user.

        Return user and followed user ids if added successfully.

        Args:
            follower_id (int): user id
            followed_id (int): followed user id

        Returns:
            Optional[Row] : user and followed user ids

        """
        fake_twitter_logger.info(
            f"Add {follower_id=} follow {followed_id=} in table "
            f"'{followers.name}'",
        )
        async with async_session() as session:
            async with session.begin():
                insert_query = (
                    PostgresqlInsert(followers).
                    values(follower_id=follower_id, followed_id=followed_id)
                )
                do_nothing_on_conflict = (
                    insert_query.
                    on_conflict_do_nothing().
                    returning(
                        followers.c.follower_id, followers.c.followed_id,
                    )
                )
                follow_query = await session.execute(do_nothing_on_conflict)
                follow_details = follow_query.one_or_none()
        fake_twitter_logger.info(f"{follow_details=}")
        return follow_details

    @staticmethod
    async def unfollow_user(
        follower_id: int, followed_id: int,
    ) -> Optional[Row]:
        """Unfollow user.

        Return user and followed user ids if entry removed successfully.

        Args:
            follower_id (int): user id
            followed_id (int): followed user id

        Returns:
            Optional[Row] : user and followed user ids

        """
        fake_twitter_logger.info(
            f"Delete {follower_id=} follow {followed_id=} in table "
            f"'{followers.name}'",
        )
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(followers).
                    where(
                        followers.c.follower_id == follower_id,
                        followers.c.followed_id == followed_id,
                    ).
                    returning(
                        followers.c.follower_id, followers.c.followed_id,
                    ),
                )
                delete_details = delete_query.one_or_none()
        fake_twitter_logger.info(f"{delete_details=}")
        return delete_details

    @classmethod
    async def get_total_followed_by_name(cls, user_name: str) -> Optional[int]:
        """Get total followed users for user with name 'user_name'.

        Return total followed users if user is existed.

        Args:
            user_name (str): user id

        Returns:
            Optional[Row] :  total followed users

        """
        fake_twitter_logger.info(
            f"Get total followed users by name {user_name=} "
            f"from table '{cls.__tablename__}'",
        )
        user = await cls.get_user_by_name(user_name)
        if user:
            total_followed = len(user.followed)
            fake_twitter_logger.info(f"{total_followed=}")
            return total_followed
        fake_twitter_logger.info(f"{user_name=} is not existed in db")
        return None


class TweetLike(Base):
    """ORM Mapped Class TweetLike, parent class Base.

    Class for creating and dealing with table 'tweets_likes'. Represent data
    about 'likes' of the tweet.

    Attributes:
        id (Optional[int]): like id, unique identifier of like
        tweet_id (int): liked tweet id
        user_name (str): name of user how liked tweet
        user_details (User): user details how liked tweet

    """

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
    UniqueConstraint(tweet_id, user_name, name="unique_tweet_like")

    @classmethod
    async def like_tweet(cls, user_name: str, tweet_id: int) -> Optional[int]:
        """Like tweet by tweet id.

        Return like id if details of tweet like inserted successfully.

        Args:
            user_name (str): username who liked tweet
            tweet_id (int): id of tweet

        Returns:
            Optional[int] : like id

        """
        fake_twitter_logger.info(f"Like {tweet_id=} by {user_name=}")
        async with async_session() as session:
            async with session.begin():
                insert_query = (
                    PostgresqlInsert(cls).
                    values(tweet_id=tweet_id, user_name=user_name)
                )
                do_nothing_on_conflict = insert_query.on_conflict_do_nothing(
                    constraint="unique_tweet_like",
                )
                like_tweet_query = await session.execute(
                    do_nothing_on_conflict.returning(cls.id),
                )
                tweet_like_id = like_tweet_query.scalar_one_or_none()
        fake_twitter_logger.info(f"{tweet_like_id=}")
        return tweet_like_id

    @classmethod
    async def dislike_tweet(
        cls, user_name: str, tweet_id: int,
    ) -> Optional[int]:
        """Dislike tweet by tweet id.

        Return like id if details of tweet like removed successfully.

        Args:
            user_name (str): username who liked tweet
            tweet_id (int): id of tweet

        Returns:
            Optional[int] : like id

        """
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(cls).
                    where(
                        cls.user_name == user_name, cls.tweet_id == tweet_id,
                    ).
                    returning(cls.id),
                )
        tweet_like_id = delete_query.scalar_one_or_none()
        return tweet_like_id

    @classmethod
    async def get_total_likes(cls) -> Optional[int]:
        """Get total likes from table.

        Returns:
            Optional[int] : total likes from table

        """
        fake_twitter_logger.info(
            f"Get total likes from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            get_query = await session.execute(
                select(func.count(cls.id)),
            )
            total_likes = get_query.scalar()
        fake_twitter_logger.info(f"{total_likes=}")
        return total_likes


class MediaFile(Base):
    """ORM Mapped Class MediaFile, parent class Base.

    Class for creating and dealing with table 'media_files'.

    Attributes:
        id (Optional[int]): media file id, unique identifier
        file_name (str): media file name
        user_name (str): name of user hom belongs media file

    """

    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(nullable=False)
    user_name: Mapped[str] = mapped_column(
        ForeignKey("users.name", ondelete="CASCADE"), nullable=False,
    )

    @classmethod
    async def add_media_file(
        cls, user_name: str, file_name: str,
    ) -> Optional[int]:
        """Add media file.

        Return media file id if added successfully.

        Args:
            user_name (str): username hom belongs file
            file_name (str): name of media file

        Returns:
            Optional[int] : media file id

        """
        fake_twitter_logger.info(
            f"Add {file_name=}, {user_name=} in table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            async with session.begin():
                add_query = await session.execute(
                    insert(cls).
                    values(user_name=user_name, file_name=file_name).
                    returning(cls.id),
                )
                media_file_id = add_query.scalar_one_or_none()
        fake_twitter_logger.info(f"Added {media_file_id=}")
        return media_file_id

    @classmethod
    async def get_total_media_files(cls) -> Optional[int]:
        """Get total number of media files.

        Returns:
            Optional[int] : total number of media files

        """
        fake_twitter_logger.info(
            f"Get total media files from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            get_query = await session.execute(
                select(func.count(cls.id)),
            )
            total_media_files = get_query.scalar_one_or_none()
        fake_twitter_logger.info(f"{total_media_files=}")
        return total_media_files

    @classmethod
    async def get_media_files_names(
        cls, ids_list: Union[list, Column],
    ) -> list:
        """Get media files names by their ids.

        Args:
            ids_list (Union[list, Column]): media files ids

        Returns:
            list : media files names

        """
        fake_twitter_logger.info(f"Get media file names for {ids_list=}")
        async with async_session() as session:
            select_query = await session.execute(
                select(cls.file_name).
                where(cls.id.in_(ids_list)),
            )
            file_names = list(select_query.scalars().all())
        fake_twitter_logger.info(f"{file_names=}")
        return file_names

    @classmethod
    async def bulk_delete(
        cls, user_name: str, files_ids: list,
    ) -> list[Optional[str]]:
        """Delete media files names by their ids.

        Args:
            user_name (str): name of user hom belongs files
            files_ids (list): media files ids

        Returns:
            list : media files names

        """
        fake_twitter_logger.info(
            f"Deleting media file {files_ids=} belong to {user_name=} "
            f"from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(cls).
                    where(cls.user_name == user_name, cls.id.in_(files_ids)).
                    returning(cls.file_name),
                )
                deleted_file_names = delete_query.scalars().all()
        fake_twitter_logger.info(f"{deleted_file_names=}")
        return list(deleted_file_names)


class Tweet(Base):
    """ORM Mapped Class Tweet, parent class Base.

    Class for creating and dealing with table 'tweets'.

    Attributes:
        id (Optional[int]): tweet id, unique identifier
        author_name (str): tweet author name
        tweet_data (str): tweet message
        tweet_media_ids (Optional[list[int]]): media ids belongs to tweet
        author (User): tweet author details
        likes(Union[list[TweetLike], list]): details of likes for the tweet

    """

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_name: Mapped[str] = mapped_column(
        ForeignKey("users.name", ondelete="CASCADE"), nullable=False,
    )
    tweet_data: Mapped[str] = mapped_column(nullable=False)
    tweet_media_ids = Column(ARRAY(Integer))
    author = relationship(
        "User",
        primaryjoin="Tweet.author_name == User.name",
        lazy="joined",
    )
    likes = relationship(
        "TweetLike",
        primaryjoin="Tweet.id == TweetLike.tweet_id",
        lazy="joined",
    )

    @classmethod
    async def add_tweet(
        cls,
        author_name: str,
        tweet_data: str,
        tweet_media_ids: Optional[list[int]] = None,
    ) -> Optional[int]:
        """Add tweet.

        Return tweet id if added successfully.

        Args:
            author_name (str): tweet author name
            tweet_data (str): tweet message
            tweet_media_ids (Optional[list[int]]=None): media ids for tweet

        Returns:
            Optional[int] : tweet id

        """
        fake_twitter_logger.info(
            f"Adding {tweet_data=}, {tweet_media_ids=}, {author_name=}"
            f"in table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            async with session.begin():
                add_query = await session.execute(
                    insert(cls).
                    values(
                        author_name=author_name,
                        tweet_data=tweet_data,
                        tweet_media_ids=tweet_media_ids,
                    ).
                    returning(cls.id),
                )
                tweet_id = add_query.scalar_one_or_none()
        fake_twitter_logger.info(f"Added {tweet_id=}")
        return tweet_id

    @classmethod
    async def delete_tweet(
        cls, author_name: str, tweet_id: int,
    ) -> Optional[Row]:
        """Delete tweet by tweet id.

        Return tweet data and media ids if removed successfully.

        Args:
            author_name (str): tweet author name
            tweet_id (int): tweet id

        Returns:
            Optional[int] : tweet data and media ids

        """
        fake_twitter_logger.info(
            f"Deleting {tweet_id=} by {author_name=} from table "
            f"'{cls.__tablename__}'",
        )
        async with async_session() as session:
            async with session.begin():
                delete_query = await session.execute(
                    delete(cls).
                    where(cls.id == tweet_id, cls.author_name == author_name).
                    returning(cls.tweet_data, cls.tweet_media_ids),
                )
                deleted_details = delete_query.one_or_none()
        fake_twitter_logger.info(f"Deleted tweet {deleted_details=}")
        return deleted_details

    @classmethod
    async def get_total_tweets(cls) -> Optional[int]:
        """Get total number of tweets.

        Returns:
            Optional[int] : total number of tweets

        """
        fake_twitter_logger.info(
            f"Get total tweets from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            select_query = await session.execute(
                select(func.count(cls.id)),
            )
            total_tweets = select_query.scalar_one_or_none()
        fake_twitter_logger.info(f"{total_tweets=}")
        return total_tweets

    # @classmethod
    # async def get_tweets_by_author_sorted_by_likes(
    #     cls, followed_names: list[str],
    # ) -> list[Optional[Tweet]]:
    #     """Get all tweets of users 'followed_names' sorted descending by
    #     likes.
    #
    #     Args:
    #         followed_names: user's names to get tweets
    #
    #     Returns:
    #         list[Tweet] : tweets
    #
    #     """
    #     fake_twitter_logger.info(
    #         f"Get tweets for {followed_names=} and sort them descending "
    #         f"by likes from table '{cls.__tablename__}'",
    #     )
    #     async with async_session() as session:
    #         select_query = await session.execute(
    #             select(cls).
    #             where(cls.author_name.in_(followed_names)).
    #             outerjoin(TweetLike, cls.id == TweetLike.tweet_id).
    #             order_by(desc(func.count(TweetLike.id))).
    #             group_by(cls.id).
    #             options(
    #                 joinedload(cls.author),
    #                 joinedload(cls.likes).
    #                 options(joinedload(TweetLike.user_details)),
    #             ),
    #         )
    #         user_tweets = select_query.unique().scalars().all()
    #     fake_twitter_logger.info(f"{user_tweets=}")
    #     return list(user_tweets)

    @classmethod
    async def get_all_tweets_sorted_by_likes(cls) -> list[Tweet]:
        """Get all tweets sorted descending by likes.

        Returns:
            list[Tweet] : all tweets

        """
        fake_twitter_logger.info(
            f"Get all tweets sorted descending by likes"
            f" from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            select_query = await session.execute(
                select(cls).
                outerjoin(TweetLike, cls.id == TweetLike.tweet_id).
                order_by(desc(func.count(TweetLike.id))).
                group_by(cls.id).
                options(
                    joinedload(cls.author),
                    joinedload(cls.likes).options(
                        joinedload(TweetLike.user_details),
                    ),
                ),
            )
            all_tweets = select_query.unique().scalars().all()
        fake_twitter_logger.info(f"{all_tweets=}")
        return list(all_tweets)


async def create_tables() -> None:
    """Create tables which are not existed in db."""
    async with async_engine.begin() as conn:
        fake_twitter_logger.info(
            "Creating tables which are not existed in db.",
        )
        await conn.run_sync(Base.metadata.create_all)
        fake_twitter_logger.info("Completed creating tables in db.")


async def init_db() -> None:
    """Initialize default data for db.

    Create and insert data in tables if User.name == test is not existed.
    """
    fake_twitter_logger.info("initializing db")
    await create_tables()
    if not await User.is_existed_user_name("test"):
        fake_twitter_logger.info("Adding default data in db")
        async with async_session() as session:
            test = User(name="test")
            alex = User(name="Alex")
            petr = User(name="Petr")
            amigo = User(name="Amigo")
            nikole = User(name="Nikole")
            alex.followed.append(petr)
            alex.followed.append(amigo)
            alex.followers.append(nikole)
            alex.followers.append(amigo)
            amigo.followed.append(petr)
            nikole.followed.append(amigo)
            nikole.followed.append(petr)
            media_file_1 = MediaFile(
                file_name="champions_1.png", user_name="Alex",
            )
            media_file_2 = MediaFile(
                file_name="champions_2.png", user_name="Alex",
            )
            media_file_3 = MediaFile(
                file_name="good_morning.jpg", user_name="Alex",
            )
            media_file_4 = MediaFile(
                file_name="sun_rise.jpg", user_name="Petr",
            )
            media_file_5 = MediaFile(
                file_name="vacation.jpg", user_name="Nikole",
            )
            tweet_1 = Tweet(
                author_name="Alex",
                tweet_data="!!!Hala Madrid!!!",
                tweet_media_ids=[1, 2],
            )
            tweet_2 = Tweet(
                author_name="Alex",
                tweet_data="Good morning=))",
                tweet_media_ids=[3],
            )
            tweet_3 = Tweet(
                author_name="Petr",
                tweet_data="Today is a nice day!",
                tweet_media_ids=[4],
            )
            tweet_4 = Tweet(
                author_name="Nikole",
                tweet_data="Awaited vacation after hard working year...",
                tweet_media_ids=[5],
            )
            tweet_5 = Tweet(
                author_name="Nikole",
                tweet_data="Again raining)",
            )
            like_1_1 = TweetLike(tweet_id=1, user_name="Nikole")
            like_2_1 = TweetLike(tweet_id=2, user_name="Nikole")
            like_2_2 = TweetLike(tweet_id=2, user_name="Amigo")
            like_3_1 = TweetLike(tweet_id=3, user_name="Nikole")
            like_3_2 = TweetLike(tweet_id=3, user_name="Amigo")
            like_3_3 = TweetLike(tweet_id=3, user_name="Alex")
            like_4_1 = TweetLike(tweet_id=4, user_name="Nikole")
            like_4_2 = TweetLike(tweet_id=4, user_name="Alex")
            session.add_all([test, alex, petr, amigo, nikole])
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
                    tweet_5,
                ],
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
                    like_4_2,
                ],
            )
            await session.commit()


async def close_db_connection() -> None:
    """Dispose connection with db."""
    fake_twitter_logger.info("Disposing async engine")
    await async_engine.dispose()
