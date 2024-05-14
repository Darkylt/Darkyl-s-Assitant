import hikari.errors
import lightbulb
import hikari

import bot_utils as utils

plugin = lightbulb.Plugin("Kick", "Kick a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.KICK_MEMBERS))

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.KICK_MEMBERS, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.KICK_MEMBERS))
@lightbulb.option("user", "The user that should be kicked", type=hikari.OptionType.USER)
@lightbulb.option("reason", "Why is the user being banned?", required=False, default=None)
@lightbulb.command("kick", "Kick a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def kick_command(ctx: lightbulb.SlashContext):
    """
    A command to kick a user.

    It processes the provided info and then kicks the user.

    Processing:
        Retreiving provided information
        Fetching the user
        Kicking the user
        Responding and logging
    """

    if not await utils.validate_command(ctx):
        return

    try:
        provided_user = ctx.options.user
        reason = ctx.options.reason

        user = await plugin.bot.application.app.rest.fetch_user(provided_user)

        guild = ctx.guild_id
        try:
            await plugin.bot.application.app.rest.kick_user(guild=guild, user=user.id, reason=reason)
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have permission to kick the user.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await ctx.respond("User has been kicked successfully.", flags=hikari.MessageFlag.EPHEMERAL)

        from bot import Logging

        await Logging.log_message(f"User <@{user.id}> has been kicked.")
    except Exception as e:
        from bot import logger
        logger.error(f"An error occured during /kick command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
