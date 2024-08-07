import config_reader as config
import hikari
import lightbulb

plugin = lightbulb.Plugin("anti_nsfw", "Prevent creation of nsfw")

ENABLED = True


@plugin.listener(hikari.events.GuildChannelUpdateEvent)
async def anti_nsfw(event: hikari.events.GuildChannelUpdateEvent) -> None:
    if ENABLED:
        if event.channel.guild_id == config.Bot.server:
            if event.channel.is_nsfw:
                await event.channel.edit(nsfw=False)
                from bot import logger

                logger.info(
                    f"Someone tried to update #{event.channel.name}({event.channel.id}) to NSFW. I reverted the change."
                )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
