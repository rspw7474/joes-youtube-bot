import asyncio

from data_handler import DataHandler
from logger import Logger
from yt_bot import YTBot
from yt_channel_fetcher import YTChannelFetcher
from yt_feed_checker import YTFeedChecker
from yt_feed_fetcher import YTFeedFetcher


async def main():
    logger = Logger()
    data_handler = DataHandler(logger)
    event_queue = asyncio.Queue()
    yt_channel_fetcher = YTChannelFetcher()
    yt_feed_fetcher = YTFeedFetcher()
    yt_feed_checker = YTFeedChecker(data_handler, event_queue, yt_feed_fetcher)
    yt_bot = YTBot(data_handler, event_queue, logger, yt_channel_fetcher, yt_feed_checker)

    async with yt_bot: 
        await yt_bot.start(yt_bot.data_handler.token)


if __name__ == "__main__":
    asyncio.run(main())
