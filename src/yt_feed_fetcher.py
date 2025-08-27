import feedparser


class YTFeedFetcher:
    def __init__(self):
        self.yt_channel_url_fragment = "https://www.youtube.com/feeds/videos.xml?channel_id="
    
    def get_yt_channel_feed(self, yt_channel_id: str) -> feedparser.util.FeedParserDict:
        yt_channel_url = self.yt_channel_url_fragment + yt_channel_id
        yt_channel_feed = feedparser.parse(yt_channel_url)
        return yt_channel_feed
