import asyncio
from youtube_bot import YouTubeBot


async def main():
    youtube_bot = YouTubeBot()
    async with youtube_bot:
        await youtube_bot.start(youtube_bot.data_handler.token)


if __name__ == "__main__":
    asyncio.run(main())
