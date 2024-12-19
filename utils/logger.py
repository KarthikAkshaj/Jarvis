import logging
import os
from datetime import datetime


class Logger:
    @staticmethod
    def setup_logging():
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"logs/jarvis_{timestamp}.log"

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        return logging.getLogger(__name__)
