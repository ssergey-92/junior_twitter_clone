"""Module with CRUD for ORM table tweets_likes."""

from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint, delete, func, select
from sqlalchemy.dialects.postgresql import Insert as PostgresqlInsert
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.project_logger import project_logger
from connection import async_session, Base


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
        project_logger.info(f"Like {tweet_id=} by {user_name=}")
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
        project_logger.info(f"{tweet_like_id=}")
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
        project_logger.info(
            f"Get total likes from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            get_query = await session.execute(
                select(func.count(cls.id)),
            )
            total_likes = get_query.scalar()
        project_logger.info(f"{total_likes=}")
        return total_likes
