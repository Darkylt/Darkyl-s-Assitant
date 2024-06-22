import hikari.errors
import lightbulb
import hikari

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("Kick", "Kick a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The user that should be banned.", required=True, type=hikari.Member)
@lightbulb.option("reason", "Why is the user being banned?", required=True, type=str)
@lightbulb.option("delete_messages", "How far back should messages be deleted?", required=False, choices=[
    "1 Hour",
    "5 Hours",
    "12 Hours",
    "1 Day",
    "2 Days",
    "3 Days",
    "4 Days",
    "5 Days",
    "6 Days",
    "7 Days"
    ], default=None)
@lightbulb.command("ban", "Ban a user", pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def ban_command(ctx: lightbulb.SlashContext, user: hikari.Member, reason: str, delete_messages):
    """
    A command to ban a user.

    It processes the provided info and then bans the user.

    Processing:
        Retreiving provided information
        Fetching the user
        Mapping of delete messages options to time durations
        Banning the user
        Responding and logging
    """

    if not await utils.validate_command(ctx):
        return

    try:
        time_durations = {
            "1 Hour": 3600,
            "5 Hours": 18000,
            "12 Hours": 43200,
            "1 Day": 86400,
            "2 Days": 172800,
            "3 Days": 259200,
            "4 Days": 345600,
            "5 Days": 432000,
            "6 Days": 518400,
            "7 Days": 604800
        }

        message_timer = time_durations.get(delete_messages, 0)
        
        try:
            await plugin.bot.application.app.rest.ban_user(guild=ctx.guild_id, user=user.id, reason=reason, delete_message_seconds=message_timer)
        except hikari.errors.ForbiddenError:
            await ctx.respond("I do not have permission to ban the user.", flags=hikari.MessageFlag.EPHEMERAL)
            return

        await ctx.respond("User has been banned successfully.", flags=hikari.MessageFlag.EPHEMERAL)
    except KeyError:
        await ctx.respond("Invalid option provided.", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred during the /ban command: {e}")
        await ctx.respond("An error occurred while processing the command.", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
