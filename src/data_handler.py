import json
import os


class DataHandler:
    def __init__(self):
        self.token = ""
        self.token_file_path = "../data/token.txt"
        self.load_token()
        self.data = {
            "latest_videos": {},
            "subscriptions": {},
            "target_channels": {}
        }
        self.data_file_paths = {
            "latest_videos": "../data/latest_videos.json",
            "subscriptions": "../data/subscriptions.json",
            "target_channels": "../data/target_channels.json"
        }
        self.load_data()

    def load_token(self):
        if os.path.exists(self.token_file_path):
            with open(self.token_file_path, "r") as f:
                self.token = f.read()
        else:
            print("{self.token_file_path} not found. Shutting down...")
            exit()

    def load_data(self):
        for data_key, file_path in self.data_file_paths.items():
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    self.data[data_key] = json.load(f)
            else:
                print(f"{file_path} not found. Proceeding without loading file...")
    
    def save_data(self, data_key: str):
        with open(self.data_file_paths[data_key], "w") as f:
            json.dump(self.data[data_key], f, indent=4)

    def clear_guild_subscriptions(self, guild_id: str) -> bool:
        try:
            del self.data["subscriptions"][guild_id]
            self.save_data("subscriptions")
            return True
        except KeyError:
            return False
    
    def clear_guild_target_channel(self, guild_id: str) -> bool:
        try:
            del self.data["target_channels"][guild_id]
            self.save_data("target_channels")
            return True
        except KeyError:
            return False
