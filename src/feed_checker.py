import asyncio
from discord.ext import commands, tasks
import feedparser


class FeedChecker:
    def __init__(self, data_handler, event_queue):
        self.data_handler = data_handler
        self.event_queue = event_queue
        self.update_interval = 300
        self.latest_videos_limit = 2

    async def produce_events(self):
        while True:
            for dc_server_id, yt_channel_ids in self.data_handler.data["subscriptions"].items():
                if not self.is_dc_channel_targeted(dc_server_id):
                    continue

                for yt_channel_id in yt_channel_ids:
                    yt_channel_feed = self.get_yt_channel_feed(yt_channel_id)
                    if not yt_channel_feed:
                        continue

                    latest_video = yt_channel_feed.entries[0]
                    latest_video_id = latest_video.yt_videoid

                    if "/shorts/" in latest_video.link:
                        continue

                    if not self.is_yt_channel_registered(yt_channel_id):
                        self.register_yt_channel(yt_channel_id)

                    if self.is_new_video(yt_channel_id, latest_video_id):
                        self.data_handler.update_latest_videos(yt_channel_id, latest_video_id)
                        self.data_handler.save_data("latest_videos")
                        event = self.produce_event(dc_server_id, yt_channel_feed.feed.title, latest_video.link)
                        await self.event_queue.put(event)

            await asyncio.sleep(self.update_interval)

    def is_dc_channel_targeted(self, dc_server_id: str) -> bool:
        if dc_server_id in self.data_handler.data["target_dc_channels"]:
            return True
        else:
            return False

    def get_yt_channel_feed(self, yt_channel_id: str) -> feedparser.util.FeedParserDict:
        yt_channel_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={yt_channel_id}"
        yt_channel_feed = feedparser.parse(yt_channel_url)
        return yt_channel_feed

    def is_yt_channel_registered(self, yt_channel_id: str) -> bool:
        if yt_channel_id in self.data_handler.data["latest_videos"]:
            return True
        else:
            return False

    def register_yt_channel(self, yt_channel_id: str) -> None:
        self.data_handler.data["latest_videos"][yt_channel_id] = []

    def is_new_video(self, yt_channel_id: str, video_id: str) -> bool:
        if video_id not in self.data_handler.data["latest_videos"][yt_channel_id]:
            return True
        else:
            return False

    def produce_event(self, dc_server_id: str, yt_channel_name: str, latest_video_link: str) -> dict:
        event = {
            "dc_server_id": dc_server_id,
            "yt_channel_name": yt_channel_name,
            "latest_video_link": latest_video_link
        }
        return event
