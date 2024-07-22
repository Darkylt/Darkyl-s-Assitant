import bot_utils as utils
import config_reader as config
import hikari
import lightbulb
import nekos

plugin = lightbulb.Plugin("why", "just why")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("why", "Askin' the real questions here")
@lightbulb.implements(lightbulb.SlashCommand)
async def why_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    try:
        await ctx.respond(nekos.why())
    except Exception as e:
        from bot import logger

        logger.error(f"An error occurred during /why: {e}")
        await ctx.respond(
            f"An error occurred!{await utils.error_fun()}",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
