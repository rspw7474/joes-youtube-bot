from datetime import datetime
import os


class Logger:
    def __init__(self):
        path_here = os.path.abspath(__file__)
        project_path = os.path.dirname(os.path.dirname(path_here))
        self.logs_file_path = project_path + "/logs/logs.txt"

    def log(self, category: str, source_function: str, message: str) -> None:
        current_date = datetime.now().date()
        current_time = datetime.now().time().strftime("%H:%M:%S")
        message = message.replace("\n", " ")
        log = f"[{current_date}][{current_time}][{category}][{source_function}] {message}"
        print(log)
        with open(self.logs_file_path, "a") as f:
            f.write(log + "\n")
