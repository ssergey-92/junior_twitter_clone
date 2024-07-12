"""Module for followers table."""

from sqlalchemy import Column, ForeignKey, Integer, Table

from connection import Base

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
