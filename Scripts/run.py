from bot import bot
from bot import purge_old_logs
from bot import logger

import config_reader as config

if __name__ == "__main__":
    try:
        config.validate()
    except Exception as e:
        logger.error(f"An error during config validation: {e}")
        exit()
    
    purge_old_logs(config.Bot.logs_folder, 30 * 24 * 3600)
    bot.load_extensions_from("./ext", recursive=True)
    bot.load_extensions_from("./AutoMod")
    bot.run()
