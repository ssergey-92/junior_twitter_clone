"""Module for creating tables and initializing default data in db."""

from app.project_logger import project_logger
from app.models.followers import followers
from app.models.media_files import MediaFile
from app.models.tweet_likes import TweetLike
from app.models.tweets import Tweet
from app.models.users import User
from connection import async_engine, async_session, Base


async def create_tables() -> None:
    """Create tables which are not existed in db."""
    async with async_engine.begin() as conn:
        project_logger.info("Creating tables which are not existed in db.")
        await conn.run_sync(Base.metadata.create_all)
    project_logger.info("Completed creating tables in db.")


async def init_db() -> None:
    """Initialize default data for db.

    Create and insert data in tables if User.name == test is not existed.

    """
    project_logger.info("initializing db")
    await create_tables()
    if not await User.is_existed_user_name("test"):
        project_logger.info("Adding default data in db")
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
                file_name="champions_1.png",
                user_name="Alex",
            )
            media_file_2 = MediaFile(
                file_name="champions_2.png",
                user_name="Alex",
            )
            media_file_3 = MediaFile(
                file_name="good_morning.jpg",
                user_name="Alex",
            )
            media_file_4 = MediaFile(
                file_name="sun_rise.jpg",
                user_name="Petr",
            )
            media_file_5 = MediaFile(
                file_name="vacation.jpg",
                user_name="Nikole",
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
