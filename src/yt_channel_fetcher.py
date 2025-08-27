import yt_dlp


class YTChannelFetcher:
    def __init__(self):
        self.ydl_opts = {"quiet": True, "extract_flat": True}

    def get_yt_channel_id(self, yt_channel_name: str) -> str | None:
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{yt_channel_name}", download=False)["entries"][0]
                return info["channel_id"]
            except:
                return None
