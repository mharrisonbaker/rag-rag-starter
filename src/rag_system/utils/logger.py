
import logging

class Logger:
    """
    A simple logger.
    This is a placeholder implementation.
    """
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, message: str):
        """Logs an info message."""
        self.logger.info(message)

    def error(self, message: str):
        """Logs an error message."""
        self.logger.error(message)
