from typing import List, Literal, Optional

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    result: Literal[True] = True


class ErrorResponse(BaseModel):
    result: Literal[False] = False
    error_type: str
    error_message: str


class AddTweetIn(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[list[int]] = None


class AddTweetOut(SuccessResponse):
    tweet_id: int


class TweetLike(BaseModel):
    user_id: int
    name: str


class UserShortDetails(BaseModel):
    id: int
    name: str


class TweetFullDetails(BaseModel):
    id: int
    content: str
    attachments: List[Optional[str]]
    author: UserShortDetails
    likes: List[Optional[TweetLike]]


class TweetFeedOut(SuccessResponse):
    tweets: List[Optional[TweetFullDetails]]


class UserDetails(UserShortDetails):
    followers: List[Optional[UserShortDetails]]
    following: List[Optional[UserShortDetails]]


class UserProfileDetailsOut(SuccessResponse):
    user: UserDetails


class AddMediaOut(SuccessResponse):
    media_id: int
