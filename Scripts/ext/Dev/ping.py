import lightbulb
import hikari
import hikari.errors

import bot_utils as utils

plugin = lightbulb.Plugin("ping", "Ping me")

@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("ping", "Ping me.", auto_defer = True, ephemeral = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ping_command(ctx: lightbulb.SlashContext) -> None:
    if not await utils.validate_command(ctx):
            return

    await ctx.respond("Pong!")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
