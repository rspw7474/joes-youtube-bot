import asyncio
from data_handler import DataHandler
from feed_checker import FeedChecker
from youtube_bot import YouTubeBot


async def main():
    data_handler = DataHandler()
    youtube_bot = YouTubeBot(data_handler)
    feed_checker = FeedChecker(youtube_bot, data_handler)
    async with youtube_bot:
        await youtube_bot.start(youtube_bot.data_handler.token)


if __name__ == "__main__":
    asyncio.run(main())
