"""Module with CRUD for ORM table tweets."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Integer,
    delete,
    desc,
    func,
    insert,
    select,
)
from sqlalchemy.engine import Row
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from app.project_logger import project_logger
from app.models.tweet_likes import TweetLike
from connection import async_session, Base


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
        project_logger.info(
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
        project_logger.info(f"Added {tweet_id=}")
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
        project_logger.info(
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
        project_logger.info(f"Deleted tweet {deleted_details=}")
        return deleted_details

    @classmethod
    async def get_total_tweets(cls) -> Optional[int]:
        """Get total number of tweets.

        Returns:
            Optional[int] : total number of tweets

        """
        project_logger.info(
            f"Get total tweets from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            select_query = await session.execute(
                select(func.count(cls.id)),
            )
            total_tweets = select_query.scalar_one_or_none()
        project_logger.info(f"{total_tweets=}")
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
    #     project_logger.info(
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
    #     project_logger.info(f"{user_tweets=}")
    #     return list(user_tweets)

    @classmethod
    async def get_all_tweets_sorted_by_likes(cls) -> list[Tweet]:
        """Get all tweets sorted descending by likes.

        Returns:
            list[Tweet] : all tweets

        """
        project_logger.info(
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
        project_logger.info(f"{all_tweets=}")
        return list(all_tweets)
