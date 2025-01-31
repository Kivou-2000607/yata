from loguru import logger
import sys
import datetime


# Remove existing log handlers to avoid duplicates
logger.remove()

# Log To Console
logger.add(sys.stderr, level="INFO")

# Add new log handler with custom settings
logger.add(
    "logs/file.{time:YYYY-MM-DD!UTC}.log",
    rotation=datetime.time(0, 0, 0, tzinfo=datetime.timezone.utc),
)


# Export the logger
__all__ = ["logger"]
