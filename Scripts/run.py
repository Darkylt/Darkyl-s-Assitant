import subprocess
import sys
import importlib
import os
import logging

from bot import bot, purge_old_logs, configure_logging
import config_reader as config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_packages(file_path):
    """
    A function for checking the installed packages and installing the missing ones

    Todo:
        Check Version as well
    """
    def read_requirements(file_path):
        """
        A helper function for reading the requirements file
        """
        try:
            with open(file_path, 'r') as file:
                return file.read().splitlines()
        except Exception as e:
            logger.error(f"An error occurred while trying to read {file_path}: {e}")
            return []

    def install_package(package_name):
        """
        A function for if a package is installed, and installing it if it isn't.
        """
        try:
            # Checking the package
            PACKAGE_NAME_MAPPING = { # Sometimes the name of the package doesn't match the import name
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

            importlib.import_module(import_name) # Trying to import module to check if it's installed
        except ImportError:
            # Installing if the package isn't found
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

    # Setup logger
    configure_logging()

    # Verifying packages
    try:
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")
        validate_packages(requirements_path)
    except Exception as e:
        logger.error(f"An error occurred during package validation: {e}")
        sys.exit(1)

    # Verifying config and other things
    try:
        config.validate()
    except Exception as e:
        logger.error(f"An error occurred during config validation: {e}")
        sys.exit(1)
    
    # Getting rid of old logs
    try:
        purge_old_logs(config.Paths.logs_folder, 30 * 24 * 3600)
    except Exception as e:
        logger.error(f"An error occurred while purging old logs: {e}")
        sys.exit(1)
    
    # Starting the bot
    try:
        bot.load_extensions_from("./ext", recursive=True)
        bot.load_extensions_from("./AutoMod")
        bot.run()
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
        sys.exit(1)
