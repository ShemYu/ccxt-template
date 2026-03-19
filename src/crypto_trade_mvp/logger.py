import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
logger.add("logs/app.log", level="DEBUG", rotation="10 MB", retention="7 days")
