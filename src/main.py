import asyncio

from data_handler import DataHandler
from feed_checker import FeedChecker
from logger import Logger
from youtube_bot import YouTubeBot
from youtube_feed_parser import YouTubeFeedParser


async def main():
    logger = Logger()
    data_handler = DataHandler(logger)
    youtube_feed_parser = YouTubeFeedParser()
    event_queue = asyncio.Queue()
    feed_checker = FeedChecker(data_handler, youtube_feed_parser, event_queue)
    youtube_bot = YouTubeBot(data_handler, feed_checker, logger, event_queue)

    async with youtube_bot: 
        await youtube_bot.start(youtube_bot.data_handler.token)


if __name__ == "__main__":
    asyncio.run(main())
