import asyncio


class FeedChecker:
    def __init__(self, data_handler, youtube_feed_parser, event_queue):
        self.data_handler = data_handler
        self.youtube_feed_parser = youtube_feed_parser
        self.event_queue = event_queue
        self.update_interval = 5
        self.latest_videos_limit = 2

    async def produce_events(self):
        while True:
            for dc_server_id in self.data_handler.list_dc_servers():
                target_dc_channel = self.data_handler.get_target_dc_channel(dc_server_id)
                if not target_dc_channel:
                    continue
                
                for yt_channel_id in self.data_handler.list_subscriptions(dc_server_id):
                    yt_channel_feed = self.youtube_feed_parser.get_yt_channel_feed(yt_channel_id)
                    if not yt_channel_feed:
                        continue

                    if not yt_channel_feed.entries:
                        continue
                    
                    latest_video = yt_channel_feed.entries[0]
                    latest_video_id = latest_video.yt_videoid

                    if "/shorts/" in latest_video.link:
                        continue

                    if self.data_handler.is_new_video(yt_channel_id, latest_video_id):
                        self.data_handler.update_latest_videos(yt_channel_id, latest_video_id)
                        event = self.produce_event(dc_server_id, yt_channel_feed.feed.title, latest_video.link)
                        await self.event_queue.put(event)

            await asyncio.sleep(self.update_interval)

    def produce_event(self, dc_server_id: str, yt_channel_name: str, latest_video_link: str) -> dict:
        event = {
            "dc_server_id": dc_server_id,
            "yt_channel_name": yt_channel_name,
            "latest_video_link": latest_video_link
        }
        return event
