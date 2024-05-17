"""Module contain validation schemas for application endpoints."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Class Settings, parent class BaseSettings.

    Class check additional parameters passed to os environ to run the
    application.

    Attributes:
        postgres_user (str): user for PostgreSQL db
        postgres_password (str): password for the above user
        postgres_db (str): name of application db
        database_url (str): url for connect to application db
        save_media_path (str): abs path where to save media files
        pytest_async_engine (Optional[bool]): flag for creation SQLAlchemy
        async engine for running Pytests.
        save_media_rel_path (Optional[str]): relative path for saving images
        while running Pytests.

    """

    postgres_user: str = Field(env="POSTGRES_USER")
    postgres_password: str = Field(env="POSTGRES_PASSWORD")
    postgres_db: str = Field(env="POSTGRES_DB")
    database_url: str = Field(env="DATABASE_URL")
    save_media_path: str = Field(env="SAVE_MEDIA_PATH")
    pytest_async_engine: Optional[bool] = Field(
        default=False, env="PYTEST_ASYNC_ENGINE",
    )
    save_media_rel_path: Optional[str] = Field(
        default="", env="SAVE_MEDIA_REL_PATH",
    )


class SuccessResponse(BaseModel):
    """Class SuccessResponse, parent class BaseModel.

    Class represent of common part of success response model for application
    endpoints.

    Attributes:
        result (Literal[True]=True): success result.

    """

    result: Literal[True] = True


class ErrorResponse(BaseModel):
    """Class ErrorResponse, parent class BaseModel.

    Class for validation response body with error message.

    Attributes:
        result (Literal[False]=False): unsuccessful result.
        error_type (str): type of error
        error_message (str):error description message

    """

    result: Literal[False] = False
    error_type: str
    error_message: str


class AddTweetIn(BaseModel):
    """Class  AddTweetIn, parent class BaseModel.

    Class for validation request body of endpoint 'add_tweet'.

    Attributes:
        tweet_data (str): tweet message
        tweet_media_ids (Optional[list[int]]=None): media ids belongs to tweet

    """

    tweet_data: str
    tweet_media_ids: Optional[list[int]] = None


class AddTweetOut(SuccessResponse):
    """Class  AddTweetOut, parent class SuccessResponse.

    Class for validation response body of endpoint 'add_tweet'.

    Attributes:
        tweet_id (int): tweet id

    """

    tweet_id: int


class TweetLikeShortDetails(BaseModel):
    """Class TweetLikeShortDetails, parent class BaseModel.

    Class for validation short details of tweet like details for validation
    class TweetFullDetails.

    Attributes:
        user_id (int): user id who liked tweet
        name (str): username who liked tweet

    """

    user_id: int
    name: str


class UserShortDetails(BaseModel):
    """Class UserShortDetails, parent class BaseModel.

    Class for validation user short details for different validation classes

    Attributes:
        id (int): user id
        name (str): username

    """

    id: int
    name: str


class TweetFullDetails(BaseModel):
    """Class TweetFullDetails, parent class BaseModel.

    Class for validation tweet details for different validation classes
    TweetFeedOut.

    Attributes:
        id (int): tweet id
        content (str): tweet message
        attachments: List[Optional[str]]: file media names belongs to tweet
        author (UserShortDetails): tweet author details
        likes: List[Optional[TweetLikeShortDetails]]: likes details

    """

    id: int
    content: str
    attachments: List[Optional[str]]
    author: UserShortDetails
    likes: List[Optional[TweetLikeShortDetails]]


class TweetFeedOut(SuccessResponse):
    """Class TweetFeedOut, parent class SuccessResponse.

    Class for validation success response body for 'get_tweet_fee' endpoint.

    Attributes:
        tweets (List[Optional[TweetFullDetails]]): tweets details

    """

    tweets: List[Optional[TweetFullDetails]]


class UserDetails(UserShortDetails):
    """Class UserDetails, parent class UserShortDetails.

    Class for validation user of validation class UserProfileDetailsOut

    Attributes:
        followers (List[Optional[UserShortDetails]]): user followers details
        following (List[Optional[UserShortDetails]]): user followed details

    """

    followers: List[Optional[UserShortDetails]]
    following: List[Optional[UserShortDetails]]


class UserProfileDetailsOut(SuccessResponse):
    """Class UserProfileDetailsOut, parent class SuccessResponse.

    Class for validation success response body for endpoints:
    'get_own_profile_details' and 'get_user_profile_details'.

    Attributes:
         user (UserDetails): user details

    """

    user: UserDetails


class AddMediaOut(SuccessResponse):
    """Class  AddMediaOut, parent class SuccessResponse.

    Class for validation success response body for endpoint: 'add_media'.

    Attributes:
         media_id (int): media file id

    """

    media_id: int
