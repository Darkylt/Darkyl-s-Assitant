import subprocess
import sys
import importlib
import os
import logging
import asyncio

from bot import bot, purge_old_logs, logger, configure_logging
import config_reader as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_packages(file_path):
    def read_requirements(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().splitlines()
        except Exception as e:
            logger.error(f"An error occurred while trying to read {file_path}: {e}")
            return []

    def install_package(package_name):
        try:

            PACKAGE_NAME_MAPPING = {
                "hikari-lightbulb": "lightbulb",
                "hikari-miru": "miru",
                "PyYAML": "yaml",
                "pillow": "PIL",
                "google-api-python-client": "googleapiclient",
                "nekos.py": "nekos",
                "webdriver-manager": "webdriver_manager",
                "lavalink-rs": "lavalink_rs"
            }

            import_name = PACKAGE_NAME_MAPPING.get(package_name, package_name)

            importlib.import_module(import_name)
        except ImportError:
            logger.info(f"{package_name} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                logger.info(f"{package_name} has been installed.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package_name}: {e}")

    packages = read_requirements(file_path)
    if not packages:
        return
    
    for package in packages:
        install_package(package.split('==')[0])

if __name__ == "__main__":

    configure_logging()

    try:
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")
        validate_packages(requirements_path)
    except Exception as e:
        logger.error(f"An error occurred during package validation: {e}")
        sys.exit(1)

    try:
        config.validate()
    except Exception as e:
        logger.error(f"An error occurred during config validation: {e}")
        sys.exit(1)
    
    try:
        purge_old_logs(config.Paths.logs_folder, 30 * 24 * 3600)
    except Exception as e:
        logger.error(f"An error occurred while purging old logs: {e}")
        sys.exit(1)
    
    try:
        bot.load_extensions_from("./ext", recursive=True)
        bot.load_extensions_from("./AutoMod")
        bot.run()
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
        sys.exit(1)
