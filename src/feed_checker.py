import asyncio
from discord.ext import commands, tasks
import feedparser
from data_handler import DataHandler


class FeedChecker:
    def __init__(self, youtube_bot: commands.Bot, data_handler: DataHandler):
        self.youtube_bot = youtube_bot
        self.data_handler = data_handler
        self.update_interval = 300
          
    async def check_feeds(self):
        await self.youtube_bot.wait_until_ready()
        while not self.youtube_bot.is_closed():
            for guild_id, channel_ids in self.data_handler.data["subscriptions"].items():
                guild = self.youtube_bot.get_guild(int(guild_id))
                if not guild:
                    continue
                
                if guild_id not in self.data_handler.data["target_channels"]:
                    continue
                
                target_channel = self.youtube_bot.get_channel(self.data_handler.data["target_channels"][guild_id])
                if not target_channel:
                    continue
                
                for channel_id in channel_ids:
                    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    feed = feedparser.parse(url)

                    if not feed.entries:
                        continue
                
                    latest_video = feed.entries[0]

                    if "/shorts/" in latest_video.link:
                        continue

                    latest_video_id = latest_video.yt_videoid

                    if channel_id not in self.data_handler.data["latest_videos"]:
                        self.data_handler.data["latest_videos"][channel_id] = []

                    if self.is_new_video(channel_id, latest_video_id):                  
                        self.update_latest_videos(channel_id, latest_video_id)
                        self.data_handler.save_data("latest_videos")
                        await target_channel.send(f"{feed.feed.title} published a new video:\n{latest_video.link}")

            await asyncio.sleep(self.update_interval)
    
    def is_new_video(self, channel_id: str, video_id: str) -> bool:
        if video_id not in self.data_handler.data["latest_videos"][channel_id]:
            return True
        else:
            return False
    
    def update_latest_videos(self, channel_id: str, video_id: str):
        self.data_handler.data["latest_videos"][channel_id].append(video_id)
        if len(self.data_handler.data["latest_videos"][channel_id]) > 2:
            self.data_handler.data["latest_videos"][channel_id].pop(0)
