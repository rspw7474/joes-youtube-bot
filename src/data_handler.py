import json
import os


class DataHandler:
    def __init__(self, logger):
        self.logger = logger
        self.token = ""
        self.load_token()
        self.data_directory_path = os.path.abspath("../data")
        self.data = {
            "latest_videos": {},
            "subscriptions": {},
            "target_dc_channels": {}
        }
        self.data_file_paths = {
            "latest_videos": self.data_directory_path + "/latest_videos.json",
            "subscriptions": self.data_directory_path + "/subscriptions.json",
            "target_dc_channels": self.data_directory_path + "/target_dc_channels.json"
        }
        self.load_data()
        self.latest_videos_limit = 2

    def load_token(self) -> None:
        try:
            self.token = os.environ["JYTB_TOKEN"]
        except KeyError:
            log_message = "Token not found. Shutting down."
            self.logger.log("ERROR", "load_token()", log_message)
            exit()

    def load_data(self) -> None:
        for data_key, file_path in self.data_file_paths.items():
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self.data[data_key] = json.load(f)
            else:
                log_message = f"\"{file_path}\" not found. Proceeding without loading file."
                self.logger.log("ALERT", "load_data()", log_message)

    def save_data(self, data_key: str) -> None:
        with open(self.data_file_paths[data_key], "w") as f:
            json.dump(self.data[data_key], f, indent=4)

    def update_latest_videos(self, yt_channel_id: str, video_id: str) -> None:
        self.data["latest_videos"][yt_channel_id].append(video_id)
        if len(self.data["latest_videos"][yt_channel_id]) > self.latest_videos_limit:
            self.data["latest_videos"][yt_channel_id].pop(0)

    def add_dc_server(self, dc_server_id: str) -> None:
        self.data["subscriptions"][dc_server_id] = []

    def add_subscription(self, yt_channel_id: str, dc_server_id: str) -> None:
        self.data["subscriptions"][dc_server_id].append(yt_channel_id)

    def remove_subscription(self, yt_channel_id: str, dc_server_id: str) -> None:
        self.data["subscriptions"][dc_server_id].remove(yt_channel_id)

    def clear_subscriptions(self, dc_server_id: str) -> bool:
        try:
            del self.data["subscriptions"][dc_server_id]
            self.save_data("subscriptions")
            return True
        except KeyError:
            return False

    def add_target_dc_channel(self, dc_server_id: str, dc_channel_id: str) -> None:
        self.data["target_dc_channels"][dc_server_id] = dc_channel_id

    def clear_target_dc_channel(self, dc_server_id: str) -> bool:
        try:
            del self.data["target_dc_channels"][dc_server_id]
            self.save_data("target_dc_channels")
            return True
        except KeyError:
            return False
    
    def remove_dc_server(self, dc_server_id: str) -> str:
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
