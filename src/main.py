import asyncio

from data_handler import DataHandler
from feed_checker import FeedChecker
from youtube_bot import YouTubeBot


async def main():
    event_queue = asyncio.Queue()
    data_handler = DataHandler()
    feed_checker = FeedChecker(data_handler, event_queue)
    youtube_bot = YouTubeBot(data_handler, feed_checker, event_queue)

    async with youtube_bot:
        await youtube_bot.start(youtube_bot.data_handler.token)


if __name__ == "__main__":
    asyncio.run(main())
