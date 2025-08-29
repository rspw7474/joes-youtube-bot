from logger import logger
import yt_dlp


class YTChannelFetcher:
    def __init__(self):
        self.ydl_opts = {"quiet": True, "extract_flat": True}

    def get_yt_channel_id(self, yt_channel_name: str) -> str | None:
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{yt_channel_name}", download=False)
                yt_channel_id = info["entries"][0]["channel_id"]
                return yt_channel_id
        except Exception as e:
            logger.error(e)
            return None
