from nonebot import get_driver, logger
from ._manager import DatabaseManager
config = get_driver().config
db_name = getattr(config, "database", "pybot.db")
db_manager = DatabaseManager(db_name, logger)
