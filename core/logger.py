import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("bsc_trading_bot")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/trade_bot.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Export for use in other modules
def get_logger(name):
    return logger.getChild(name)
