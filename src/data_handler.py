import json
from logger import logger
import os


class DataHandler:
    def __init__(self):
        self.token = ""
        self.load_token()
        self.data = {
            "latest_videos": {},
            "subscriptions": {},
            "target_dc_channels": {}
        }
        data_directory_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data"
        os.makedirs(data_directory_path, exist_ok=True)
        self.data_file_paths = {
            "latest_videos": data_directory_path + "/latest_videos.json",
            "subscriptions": data_directory_path + "/subscriptions.json",
            "target_dc_channels": data_directory_path + "/target_dc_channels.json"
        }
        self.load_data()

    def load_token(self) -> None:
        self.token = os.environ.get("JYTB_TOKEN")
        if not self.token:
            log_message = "Token not found. Shutting down."
            logger.error(log_message)
            exit()

    def save_data(self, data_key: str) -> None:
        with open(self.data_file_paths[data_key], "w") as f:
            json.dump(self.data[data_key], f, indent=4)

    def load_data(self) -> None:
        for data_key, file_path in self.data_file_paths.items():
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self.data[data_key] = json.load(f)
            else:
                log_message = f"\"{file_path}\" not found. Proceeding without loading file."
                logger.warning(log_message)

    def add_target_dc_channel(self, dc_server_id: str, dc_channel_id: str) -> bool:
        if dc_server_id in self.data["target_dc_channels"]:
            return False

        self.data["target_dc_channels"][dc_server_id] = dc_channel_id
        self.save_data("target_dc_channels")
        return True

    def get_target_dc_channel(self, dc_server_id: str) -> str | None:
        return self.data["target_dc_channels"].get(dc_server_id)

    def clear_target_dc_channel(self, dc_server_id: str) -> bool:
        if not dc_server_id in self.data["target_dc_channels"]:
            return False

        del self.data["target_dc_channels"][dc_server_id]
        self.save_data("target_dc_channels")
        return True

    def add_subscription(self, yt_channel_id: str, dc_server_id: str) -> bool:
        if not dc_server_id in self.data["subscriptions"]:
            self.data["subscriptions"][dc_server_id] = []

        if yt_channel_id in self.data["subscriptions"][dc_server_id]:
            return False

        self.data["subscriptions"][dc_server_id].append(yt_channel_id)
        self.save_data("subscriptions")
        return True

    def list_subscriptions(self, dc_server_id: str) -> list[str]:
        return self.data["subscriptions"].get(dc_server_id, [])

    def remove_subscription(self, yt_channel_id: str, dc_server_id: str) -> bool:
        if dc_server_id not in self.data["subscriptions"]:
            return False

        if not yt_channel_id in self.data["subscriptions"][dc_server_id]:
            return False

        self.data["subscriptions"][dc_server_id].remove(yt_channel_id)
        self.save_data("subscriptions")
        return True

    def clear_subscriptions(self, dc_server_id: str) -> bool:
        if not dc_server_id in self.data["subscriptions"]:
            return False

        del self.data["subscriptions"][dc_server_id]
        self.save_data("subscriptions")
        return True

    def list_dc_servers(self) -> list[str]:
        return list(self.data["subscriptions"])

    def remove_dc_server(self, dc_server_id: str) -> bool:
        removed_data = False
        if dc_server_id in self.data["subscriptions"]:
            del self.data["subscriptions"][dc_server_id]
            self.save_data("subscriptions")
            removed_data = True

        if dc_server_id in self.data["target_dc_channels"]:
            del self.data["target_dc_channels"][dc_server_id]
            self.save_data("target_dc_channels")
            removed_data = True

        return removed_data

    def is_new_video(self, yt_channel_id: str, video_datetime: str) -> bool:
        last_video_datetime = self.data["latest_videos"].get(yt_channel_id)
        if last_video_datetime is None or video_datetime > last_video_datetime:
            return True
        else:
            return False

    def update_latest_videos(self, yt_channel_id: str, video_datetime: str) -> None:
        self.data["latest_videos"][yt_channel_id] = video_datetime
        self.save_data("latest_videos")
