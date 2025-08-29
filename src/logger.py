import logging
import os


def create_logger() -> logging.Logger:
    logs_directory_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/logs"
    logs_file_path = logs_directory_path + "/logs.txt"
    os.makedirs(logs_directory_path, exist_ok=True)

    logger = logging.getLogger("ytb")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_file_path)
        ]
    )
    return logger

logger = create_logger()
