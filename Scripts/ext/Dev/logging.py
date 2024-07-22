import config_reader as config
import hikari
import lightbulb
from bot import Logging

plugin = lightbulb.Plugin("logging", "Logging events")


@plugin.listener(hikari.BanCreateEvent)
async def on_ban(event: hikari.BanCreateEvent):
    """
    A function for logging a ban
    """
    ban = await event.fetch_ban()

    await plugin.app.rest.create_message(
        config.Bot.logs_channel,
        f"{ban.user.username} was banned for {ban.reason}",
        user_mentions=False,
        mentions_everyone=False,
        mentions_reply=False,
    )


@plugin.listener(hikari.BanDeleteEvent)
async def on_unban(event: hikari.BanDeleteEvent):
    """
    A function for logging an unban
    """
    user = await event.fetch_user()

    await plugin.app.rest.create_message(
        config.Bot.logs_channel,
        f"{user.username} was unbanned.",
        user_mentions=False,
        mentions_everyone=False,
        mentions_reply=False,
    )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
