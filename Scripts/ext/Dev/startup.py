import asyncio

import buttons
import hikari
import lightbulb
import miru
import timed_events
import youtube

plugin = lightbulb.Plugin("startup", "Containing functions called at startup")


async def wait_until_initialized():
    """
    Wait until the bot is fully initialized and bot.application.app exists.
    """
    while not (
        hasattr(plugin.bot, "application")
        and getattr(plugin.bot.application, "app", None)
    ):
        await asyncio.sleep(1)


@plugin.listener(hikari.StartedEvent)
async def on_startup(event: hikari.StartedEvent):
    """
    Gets called when the bot starts.
    """
    from bot import logger

    logger.info("Bot is online")

    # Set status
    try:
        await plugin.bot.update_presence(
            status=hikari.Status.ONLINE,
            activity=hikari.Activity(name="Darkyl", type=hikari.ActivityType.LISTENING),
        )
    except Exception as e:
        logger.error(f"An error occurred during startup while updating presence: {e}")

    # Start button views
    try:
        await buttons.ManageViews.start_views(
            miru.Client(plugin.bot),
            views=[
                buttons.VerifyView,
                buttons.ReactionRoles.Descriptor,
                buttons.ReactionRoles.Pronouns,
                buttons.ReactionRoles.Region,
                buttons.ReactionRoles.Pings,
                buttons.Report,
                buttons.Worm,
                buttons.ModMenu,
                buttons.NSFWOptIn,
                buttons.NSFWOptOut,
                buttons.RockPaperScissors,
                buttons.RockPaperScissorsReplay,
                buttons.Confess,
                buttons.Test,
                buttons.HelpMenu,
            ],
        )

    except Exception as e:
        logger.error(f"An error occurred during startup while starting views: {e}")

    await wait_until_initialized()

    # Running background tasks
    try:
        asyncio.create_task(youtube.run(plugin.bot))
        asyncio.create_task(timed_events.run_events(plugin.bot))
    except Exception as e:
        logger.error(f"An error occurred during startup while starting timers: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
