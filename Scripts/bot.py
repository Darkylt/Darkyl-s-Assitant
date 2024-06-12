import os
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import warnings
import glob
import time

import hikari
import hikari.channels
import hikari.errors
import hikari.permissions
import lightbulb
import miru
import lavalink_rs

import config_reader as config
import buttons
import youtube
import timed_events
import error_handler

warnings.filterwarnings("ignore", category=DeprecationWarning)

class Bot(lightbulb.BotApp):
    __slots__ = ("lavalink",)

    def __init__(self) -> None:
        super().__init__(
            token=config.Bot.token,
            default_enabled_guilds=(config.Bot.server, 811591956668219422),
            intents=hikari.Intents.ALL
        )

        self.lavalink = lavalink_rs.LavalinkClient

bot = Bot()

miru_client = miru.Client(bot)

logging.basicConfig(level=logging.DEBUG)  # Set the default logging level
       
# Clear latest.log before writing to it
with open(os.path.join(config.Paths.logs_folder, "latest.log"), 'w'):
    pass

def purge_old_logs(logs_folder, retention_period):
    current_time = time.time()
    for file_path in glob.glob(os.path.join(logs_folder, "*.log")):
        if os.stat(file_path).st_mtime < current_time - retention_period:
            os.remove(file_path)

def configure_logging():
    latest_file_handler = logging.FileHandler(os.path.join(config.Paths.logs_folder, "latest.log"))
    latest_file_handler.setLevel(logging.DEBUG)
    # Create a TimedRotatingFileHandler to create log files with timestamps (e.g., 2024-05-03_12-00-00.log)
    filename = os.path.join(config.Paths.logs_folder, f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
    time_file_handler = TimedRotatingFileHandler(filename=filename, when='midnight', interval=1, backupCount=7)
    time_file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler
    # Create a formatter to specify the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Attach the formatter to each file handler
    latest_file_handler.setFormatter(formatter)
    time_file_handler.setFormatter(formatter)
    # Get the root logger and add the file handlers to it
    root_logger = logging.getLogger()
    root_logger.addHandler(latest_file_handler)
    root_logger.addHandler(time_file_handler)

logger = logging.getLogger(__name__)

class Logging():
    """
    A class used for the bots logging.
    """

    async def log_message(log: str):
        """
        Sends a message into the logs channel on discord
        Args:
            log (str): The message
        """

        try:
            await bot.application.app.rest.create_message(config.Bot.logs_channel, log)
        except Exception as e:
            logger.error(f"Following error occured during log message: {e}")

@bot.listen(hikari.StartedEvent)
async def on_startup(event: hikari.StartedEvent):
    """
    Gets called when the bot starts.

    Current operations:
        Logs: Configures the logging
        Status: Sets the bot's status to online
        Buttons: Starts the Views so the buttons continue working
        YouTube: Starts the YouTube checks
        Events: Starts the Event loops
    """
    logger.info("Bot is online")

    try:
        await bot.update_presence(status=hikari.Status.ONLINE, activity=hikari.Activity(name="Darkyl", type=hikari.ActivityType.LISTENING))
    except Exception as e:
        logger.error(f"An error occurred during startup while updating presence: {e}")

    try:
        await buttons.ManageViews.start_views(
            miru_client,
            views=[
                buttons.VerifyView,
                buttons.ReactionRoles.Descriptor,
                buttons.ReactionRoles.Pronouns,
                buttons.ReactionRoles.Region,
                buttons.Report,
                buttons.Worm,
                buttons.ModMenu,
                buttons.NSFWOptIn,
                buttons.NSFWOptOut,
                buttons.RockPaperScissors,
                buttons.RockPaperScissorsReplay
            ]
        )
    except Exception as e:
        logger.error(f"An error occurred during startup while starting views: {e}")

    try:
        asyncio.create_task(youtube.run(bot))
        asyncio.create_task(timed_events.run_events(bot))
    except Exception as e:
        logger.error(f"An error occurred during startup while starting timers: {e}")

@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent):
    await error_handler.on_error(event=event)

@bot.listen(hikari.BanCreateEvent)
async def on_ban(event: hikari.BanCreateEvent):
    ban = await event.fetch_ban()

    await Logging.log_message(f"{ban.user.username} was banned for {ban.reason}")

@bot.listen(hikari.BanDeleteEvent)
async def on_unban(event: hikari.BanDeleteEvent):
    user = await event.fetch_user()

    await Logging.log_message(f"{user.username} was unbanned.")
