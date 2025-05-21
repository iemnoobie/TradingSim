import logging
from pathlib import Path
from dotenv import load_dotenv
import os

def setup_logger(name: str, log_file: str = "logs/app.log", level=logging.INFO):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

# Load environment variables
load_dotenv()

def get_api_credentials():
    return {
        "api_key": os.getenv("OKX_API"),
        "secret_key": os.getenv("OKX_SECRET_KEY")
    }
