import asyncio
import os

from data_handler import DataHandler
from logger import logger
from yt_bot import YTBot
from yt_channel_fetcher import YTChannelFetcher
from yt_feed_checker import YTFeedChecker
from yt_feed_fetcher import YTFeedFetcher


async def main():
    data_handler = DataHandler()
    event_queue = asyncio.Queue()

    yt_channel_fetcher = YTChannelFetcher()
    yt_feed_fetcher = YTFeedFetcher()
    yt_feed_checker = YTFeedChecker(data_handler, event_queue, yt_feed_fetcher)
    yt_bot = YTBot(data_handler, event_queue, yt_channel_fetcher, yt_feed_checker)

    async with yt_bot: 
        await yt_bot.start(yt_bot.data_handler.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(e)
