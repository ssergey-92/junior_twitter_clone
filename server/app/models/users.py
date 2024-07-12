"""Module with CRUD for ORM table users."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import Insert as PostgresqlInsert
from sqlalchemy.engine import Row
from sqlalchemy.orm import (
    Mapped,
    backref,
    joinedload,
    mapped_column,
    relationship,
)
from app.project_logger import project_logger
from app.models.followers import followers
from connection import async_session, Base


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
        project_logger.info(
            f"Checking if {user_name=} is existed in table "
            f"'{cls.__tablename__}'",
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User.id).where(User.name == user_name),
            )
            user_id = user_query.scalar_one_or_none()
        project_logger.info(f"Details of {user_name=}: {user_id=}")
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
        project_logger.info(
            f"Get user id by {user_name=} from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            user_query = await session.execute(
                select(User.id).where(User.name == user_name),
            )
            user_id = user_query.scalar_one_or_none()
        project_logger.info(f"{user_name=}: {user_id=}")
        return user_id

    @classmethod
    async def add_user(cls, user_name: str) -> None:
        """Add new user.

        Args:
            user_name (str): username

        """
        project_logger.info(
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
        project_logger.info(
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
        project_logger.info(f"Details of {user_name=}: {user}")
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
        project_logger.info(
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
        project_logger.info(f"Details {user_id=}: {user}")
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
        project_logger.info(
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
        project_logger.info(f"{follow_details=}")
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
        project_logger.info(
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
        project_logger.info(f"{delete_details=}")
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
        project_logger.info(
            f"Get total followed users by name {user_name=} "
            f"from table '{cls.__tablename__}'",
        )
        user = await cls.get_user_by_name(user_name)
        if user:
            total_followed = len(user.followed)
            project_logger.info(f"{total_followed=}")
            return total_followed
        project_logger.info(f"{user_name=} is not existed in db")
        return None
