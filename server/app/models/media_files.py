"""Module with CRUD for ORM table media_files."""

from typing import Optional, Union

from sqlalchemy import Column, ForeignKey, delete, func, insert, select
from sqlalchemy.orm import Mapped, mapped_column

from app.project_logger import project_logger
from connection import async_session, Base


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
        project_logger.info(
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
        project_logger.info(f"Added {media_file_id=}")
        return media_file_id

    @classmethod
    async def get_total_media_files(cls) -> Optional[int]:
        """Get total number of media files.

        Returns:
            Optional[int] : total number of media files

        """
        project_logger.info(
            f"Get total media files from table '{cls.__tablename__}'",
        )
        async with async_session() as session:
            get_query = await session.execute(
                select(func.count(cls.id)),
            )
            total_media_files = get_query.scalar_one_or_none()
        project_logger.info(f"{total_media_files=}")
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
        project_logger.info(f"Get media file names for {ids_list=}")
        async with async_session() as session:
            select_query = await session.execute(
                select(cls.file_name).
                where(cls.id.in_(ids_list)),
            )
            file_names = list(select_query.scalars().all())
        project_logger.info(f"{file_names=}")
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
        project_logger.info(
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
        project_logger.info(f"{deleted_file_names=}")
        return list(deleted_file_names)
