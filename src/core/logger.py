"""
Logging configuration for the application.
Logs are written to patreon_scrape.log for debugging.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class AppLogger:
    """Application logger singleton."""

    _instance: Optional['AppLogger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'AppLogger':
        """Singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger if not already initialized."""
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure the logger with file and console handlers."""
        # Create logger
        self._logger = logging.getLogger('patreon_scrape')
        self._logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if self._logger.handlers:
            return

        # Create logs directory if it doesn't exist
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File handler - detailed logs
        log_file = os.path.join(log_dir, 'patreon_scrape.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler - only warnings and errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

        # Log startup
        self._logger.info("="*80)
        self._logger.info(f"Logging initialized at {datetime.now()}")
        self._logger.info("="*80)

    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        if self._logger is None:
            self._setup_logger()
        return self._logger  # type: ignore


# Global logger instance
def get_logger() -> logging.Logger:
    """Get the application logger."""
    return AppLogger().get_logger()
