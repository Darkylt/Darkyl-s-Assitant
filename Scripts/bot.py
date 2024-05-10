import os
import asyncio
import json
import sys
import subprocess
import aiohttp
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import re
import warnings
import random
import datetime

import hikari
import hikari.channels
import hikari.permissions
import lightbulb
import miru
import nekos

import config_reader as config
import member_managment
import buttons
import youtube
import timed_events
import bot_utils as utils
import image_manager
import error_handler
import auto_mod
import UtilityCommandFunctions
from Worm import worm_simulator

warnings.filterwarnings("ignore", category=DeprecationWarning)

bot = lightbulb.BotApp(
    token=config.Bot.token,
    default_enabled_guilds=(config.Bot.server, 811591956668219422),
    intents=hikari.Intents.ALL
)

bot.load_extensions_from("./ext", recursive=True)

miru_client = miru.Client(bot)

logging.basicConfig(level=logging.DEBUG)  # Set the default logging level
            
# Clear latest.log before writing to it
with open(os.path.join(config.Bot.logs_folder, "latest.log"), 'w'):
    pass
            
latest_file_handler = logging.FileHandler(os.path.join(config.Bot.logs_folder, "latest.log"))
latest_file_handler.setLevel(logging.DEBUG)
# Create a TimedRotatingFileHandler to create log files with timestamps (e.g., 2024-05-03_12-00-00.log)
filename = os.path.join(config.Bot.logs_folder, f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
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

    try:
        await bot.update_presence(status=hikari.Status.ONLINE, activity=hikari.Activity(name="Darkyl", type=hikari.ActivityType.LISTENING))

        await buttons.ManageViews.start_views(
            client=miru_client,
            views=[
                buttons.VerifyView,
                buttons.ReactionRoles.Descriptor,
                buttons.ReactionRoles.Pronouns,
                buttons.ReactionRoles.Region,
                buttons.Report,
                buttons.Worm
            ]
        )

        asyncio.create_task(youtube.run(bot))
        asyncio.create_task(timed_events.run_events(bot))

        logger.info("Bot is online")
    
    except Exception as e:
        logger.error(f"An error occurred during startup: {e}")

@bot.listen(hikari.MemberCreateEvent)
async def handle_join(event: hikari.MemberCreateEvent):
    """
    Get's called when a new member joins.
    It runs a helper function used for handling new joins.
    """
    try:
        if event.member.is_bot or event.member.is_system:
            return
        
        await member_managment.new_member(event, bot)
    except Exception as e:
        logger.error(f"Error during member join event: {e}")

@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent):
    await error_handler.on_error(event=event)

@bot.listen(hikari.MessageCreateEvent)
async def message(event: hikari.MessageCreateEvent):
    """Gets called whenever a message is sent."""
    try:
        channel = await bot.application.app.rest.fetch_channel(event.message.channel_id)
        channel_type = str(channel.type)

        if channel_type == "DM":
            await handle_dm(event)
        elif channel_type == "GUILD_TEXT":
            await handle_guild_text(event, nsfw=channel.is_nsfw)
    except Exception as e:
        logger.error(f"An error occurred while handling a message: {e}")

async def handle_dm(event: hikari.MessageCreateEvent):
    """Handles direct messages."""
    if event.author.is_bot or event.author.is_system:
        return
    
    await event.message.respond("Heya! DM interactions aren't implemented yet.\nIf you have an idea for DM interactions, tell it Darkyl!")

async def handle_guild_text(event: hikari.MessageCreateEvent, nsfw: bool):
    """Handles messages in guild text channels."""
    try:
        #if event.message.guild_id != config.Bot.server:
        #    return

        if event.author.is_bot or event.author.is_system:
            return

        violations = await auto_mod.check_message(content=event.message.content, nsfw=nsfw)

        if violations:
            report_embed = await auto_mod.handle_violations(event, violations)
            await send_report(event, report_embed)
            auto_mod.update_report_data(event, event.message.id, violations)
            await event.message.delete()

        await member_managment.update_user_stats(
            user_id=event.author_id,
            msg=True,
            cmd=False,
            rep=False,
            created_at=str(event.message.author.created_at)
        )
    except Exception as e:
        logger.error(f"Error during handle_guild_text: {e}")

async def send_report(event: hikari.MessageCreateEvent, report_embed: hikari.Embed) -> hikari.Message:
    """Sends the violation report to the designated channel."""
    view = buttons.Report()
    message = await bot.application.app.rest.create_message(channel=config.Bot.report_channel, embed=report_embed, components=view)
    return message

@bot.listen(hikari.GuildMessageDeleteEvent)
async def on_guild_msg_delete(event: hikari.GuildMessageDeleteEvent):
    try:
        msg = event.old_message

        if msg.author.is_bot or msg.author.is_system:
            return
        
        if not msg.guild_id == config.Bot.server:
            return
        
        name = msg.author.username
        mention = msg.author.mention
        content = msg.content
        try:
            attach = msg.attachments[0]
            attachment_file = attach.url or attach.proxy_url
        except(IndexError, KeyError):
            attachment_file = None
        
        embed = hikari.Embed(title="A message has been deleted.", description=f"{mention}'s message has been deleted.", color=(hikari.Color.from_rgb(255, 0, 0)))
        embed.add_field(name="Author:", value=name)
        embed.add_field(name="Content:", value=content)

        if attachment_file == None:
            await bot.application.app.rest.create_message(channel=config.Bot.logs_channel, embed=embed)
        else:
            await bot.application.app.rest.create_message(channel=config.Bot.logs_channel, embed=embed, attachments=attachment_file)
    except Exception as e:
        logger.error(f"Error while logging deleted message: {e}")
        return

@bot.listen(hikari.BanCreateEvent)
async def on_ban(event: hikari.BanCreateEvent):
    ban = await event.fetch_ban()

    await Logging.log_message(f"{ban.user.username} was banned for {ban.reason}")

@bot.listen(hikari.BanDeleteEvent)
async def on_unban(event: hikari.BanDeleteEvent):
    user = await event.fetch_user()

    await Logging.log_message(f"{user.username} was unbanned.")

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("admin_stop", "Stop the Bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def stop_command(ctx: lightbulb.SlashContext) -> None:
    """
    A command that shuts down the bot.
    It checks if the command is executed by darkyl and then gracefully shuts down the bot.
    """

    try:
        if ctx.author.id == config.Bot.darkyl_id: # Check if the command is executed by the right person
            await ctx.respond("Bot is shutting down.", flags=hikari.MessageFlag.EPHEMERAL)

            logger.info(f"{ctx.author.id} executed /{ctx.command.name}")

            await bot.update_presence(status=hikari.Status.OFFLINE)

            await bot.close()

            await Logging.log_message("Bot shut down by command.")
            logger.info(f"Bot shut down by command.")
        else:
            await ctx.respond("You are not permitted to shut down the Bot", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occurred during the /admin_stop command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

async def restart():
    """
    A helper function used for restarting the bot
    """
    try:
        logger.info("Bot restarts by command.")
        await bot.close()
        executable = sys.executable
        subprocess.Popen([executable, __file__])
    except Exception as e:
        logger.error(f"An error occurred during restart: {e}")

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("admin_restart", "Restart the Bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def restart_command(ctx: lightbulb.SlashContext) -> None:
    """
    A command that restarts the bot.
    It checks if the command is executed by darkyl and then calls the restart function.
    """

    try:
        if ctx.author.id == config.Bot.darkyl_id:
            await ctx.respond("Bot is restarting.", flags=hikari.MessageFlag.EPHEMERAL)

            logger.info(f"{ctx.author.id} executed /{ctx.command.name}")

            await Logging.log_message("Restarting...")

            await bot.update_presence(status=hikari.Status.OFFLINE)

            await restart()
    except Exception as e:
        logger.error(f"An error occurred during /admin_restart command: {e}")
        await ctx.respond("An error occurred.", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
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

        user = await bot.application.app.rest.fetch_user(provided_user)

        guild = ctx.guild_id

        await bot.application.app.rest.kick_user(guild=guild, user=user.id, reason=reason)

        await ctx.respond("User has been kicked successfully.", flags=hikari.MessageFlag.EPHEMERAL)

        await Logging.log_message(f"User <@{user.id}> has been kicked.")
    except Exception as e:
        logger.error(f"An error occured during /kick command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
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
@lightbulb.command("ban", "Ban a user")
@lightbulb.implements(lightbulb.SlashCommand)
async def ban_command(ctx: lightbulb.SlashContext):
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
    try:
        if not await utils.validate_command(ctx):
            return

        # Options
        provided_user = ctx.options.user
        reason = ctx.options.reason
        delete_messages = ctx.options.delete_messages

        user = await ctx.app.rest.fetch_user(provided_user)

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

        guild = ctx.guild_id

        await ctx.app.rest.ban_user(guild=guild, user=user.id, reason=reason, delete_message_seconds=message_timer)

        await ctx.respond("User has been banned successfully.", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occurred during the /ban command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("user", "The user that should be warned", type=hikari.OptionType.USER)
@lightbulb.option("reason", "Warning", type=str)
@lightbulb.command("warn", "Warn a member")
@lightbulb.implements(lightbulb.SlashCommand)
async def warn_command(ctx: lightbulb.SlashContext):
    """
    A command to warn a user.

    It processes the provided info and then warns the user.

    Processing:
        Retreiving provided information
        Fetching the user
        Reads the existing warnings
        Adds the new reason
        Updates the file
        Checks if the user is to be banned or kicked
        Performs these actions, responds with sucess if not
    """
    if not await utils.validate_command(ctx):
        return

    try:
        provided_user = ctx.options.user
        reason = ctx.options.reason

        user = await bot.application.app.rest.fetch_user(provided_user)

        user_id = str(user.id)  # Convert user ID to string

        # Load existing data from the JSON file if it exists and is not empty
        database_path = os.path.join(config.Bot.data_folder, "User Data", "warnings.json")
        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        # Check if user already exists in the data dictionary
        if user_id in data:
            # Append new reason to existing list of reasons
            data[user_id].append(reason)
        else:
            # Create a new entry with the user ID and a list containing the new reason
            data[user_id] = [reason]

        # Write the updated data back to the JSON file
        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)
        
        if len(data.get(user_id, [])) > 2 and len(data.get(user_id, [])) < 4:
            await bot.application.app.rest.kick_user(ctx.guild_id, user_id, reason="Too many warnings.")
            await Logging.log_message(f"User <@{user_id}> has been kicked.")
            await ctx.respond(f"Warned <@{user_id}> for '{reason}'.\n\n(User was kicked for too many warnings)", flags=hikari.MessageFlag.EPHEMERAL)
        elif len(data.get(user_id, [])) > 4:
            await bot.application.app.rest.ban_user(ctx.guild_id, user_id, reason="Too many warnings.")
            await Logging.log_message(f"User <@{user_id}> has been banned.")
            await ctx.respond(f"Warned <@{user_id}> for '{reason}'.\n\n(User was banned for too many warnings)", flags=hikari.MessageFlag.EPHEMERAL)
        else:
            await ctx.respond(f"Warned <@{user_id}> for '{reason}'.", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occurred while warning a user: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.BAN_MEMBERS))
@lightbulb.option("user", "The user that should have their warning cleared", type=hikari.Member)
@lightbulb.command("clear_warnings", "Remove all warnings of someone")
@lightbulb.implements(lightbulb.SlashCommand)
async def clear_warnings_command(ctx: lightbulb.SlashContext):
    """
    A command to clear all warnings of a user.

    Processing:
        It fetches the provided user
        Reads the existing entries
        Deletes all warnings
        Writes the updated file
        Responds
    """



    if not await utils.validate_command(ctx):
        return

    try:
        provided_user = ctx.options.user

        user = await bot.application.app.rest.fetch_user(provided_user)

        user_id = str(user.id)

        # Load existing data from the JSON file
        database_path = os.path.join(config.Bot.data_folder, "User Data", "warnings.json")
        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        else:
            # No data in the file
            data = {}

        # Remove the user's entry from the data dictionary if it exists
        if user_id in data:
            del data[user_id]

        # Write the updated data back to the JSON file
        with open(database_path, "w") as file:
            json.dump(data, file, indent=4)

        await ctx.respond(f"Successfully removed all warnings for {user.username}", flags=hikari.MessageFlag.EPHEMERAL)
        await Logging.log_message(f"User <@{user_id}> has had all their warnings removed.")
    except Exception as e:
        logger.error(f"An error occurred while clearing warnings: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("interval", "The interval amount (in seconds)",type=int, min_value = 0, max_value = 21600, required=True)
@lightbulb.option("channel", "The channel you want to set", hikari.TextableGuildChannel, required=False)
@lightbulb.app_command_permissions(hikari.permissions.Permissions.MANAGE_CHANNELS, dm_enabled=False)
@lightbulb.command("slowmode", "Set the slowmode interval for a channel", pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def slowmode_command(ctx: lightbulb.SlashContext, channel: hikari.TextableGuildChannel, interval: int):
    """
    A command to set the slowmode for a channel

    Processing:
        Gets the provided info and performs some basic checks
        Applies the slowmode
        Responds
    """

    if not await utils.validate_command(ctx):
        return

    time = interval

    if channel == None:
        channel=ctx.get_channel()

    if time < 0:
        await ctx.respond(f"The parameter 'interval' has to be a positive number", flags=hikari.MessageFlag.EPHEMERAL)

    try:
        await ctx.bot.rest.edit_channel(channel, rate_limit_per_user=time)
    except Exception as e:
        logger.error(f"An error occcurred while attempting to set slowmode: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

    if time == 0:
        await ctx.respond(f"Removed slow mode from selected {channel.mention}", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        if time > 1:
            await ctx.respond(f"Slowmode of {time} seconds has been set for {channel.mention}", flags=hikari.MessageFlag.EPHEMERAL)
        if time <= 1:
            await ctx.respond(f"Slowmode of {time} second has been set for {channel.mention}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.permissions.Permissions.MODERATE_MEMBERS, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MODERATE_MEMBERS))
@lightbulb.option("reason", "the reason for the timeout", type=str, required=False)
@lightbulb.option("days", "the duration of the timeout (days)", type=int, required=False, default=0)
@lightbulb.option("hours", "the duration of the timeout (hour)", type=int, required=False, default=0)
@lightbulb.option("minutes", "the duration of the timeout (minute)", type=int, required=False, default=0)
@lightbulb.option("seconds", "the duration of the timeout (second)", type=int, required=False, default=0)
@lightbulb.option("user", "the user you want to be put in timeout", type=hikari.Member , required=True)
@lightbulb.command("timeout", "Timeout a member")
@lightbulb.implements(lightbulb.SlashCommand)
async def timeout_command(ctx: lightbulb.SlashContext):
    """
    A command to timeout a user

    Processing:
        Get the amount of time to timeout for
        Apply the timeout
        Respond
    """

    user = ctx.options.user
    seconds = ctx.options.seconds
    minutes = ctx.options.minutes
    hours = ctx.options.hours
    days = ctx.options.days
    reason = ctx.options.reason

    if not await utils.validate_command(ctx):
        return

    reason = reason or f"No Reason Provided."
    now = datetime.datetime.now()
    then = now + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    if (then - now).days > 28:
        await ctx.respond("You can't time someone out for more than 28 days", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    try:
        await ctx.bot.rest.edit_member(user=user, guild=ctx.get_guild(), communication_disabled_until=then, reason=reason)
    except Exception as e:
        logger.error(f"An error occurred while trying to timeout user: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    try:
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            await ctx.respond(f"Removing timeout from **{user.mention}**", flags=hikari.MessageFlag.EPHEMERAL)
            await Logging.log_message(f"The user {user.mention} had their timeout removed.")
        else:
            await ctx.respond(f"The user {user.mention} has been timed out until <t:{int(then.timestamp())}:R> for `{reason}`", flags=hikari.MessageFlag.EPHEMERAL)
            await Logging.log_message(f"The user {user.mention} has been timed out until <t:{int(then.timestamp())}:R> for `{reason}`")
    except Exception as e:
        logger.error(f"Error during /timeout while responding: {e}")

@bot.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("channel", "The channel you want to set", hikari.TextableGuildChannel, required=False)
@lightbulb.option("amount", "The number of messages to purge.", type=int, required=True, max_value = 500)
@lightbulb.app_command_permissions(hikari.permissions.Permissions.MANAGE_MESSAGES, dm_enabled=False)
@lightbulb.command("purge", "Purge messages from this channel.", aliases=["clear","prune"], auto_defer = True, pass_options = True)
@lightbulb.implements(lightbulb.SlashCommand)
async def purge_command(ctx: lightbulb.SlashContext, channel: hikari.TextableGuildChannel, amount: int) -> None:
    """
    Deletes all messages from a channel

    Processing:
        Performs some quick checks on the inputs
        Fetches all the messages that fit the criteria
        Deletes them
        Responds
    """
    if not await utils.validate_command(ctx):
        return

    if amount > 500:
        await ctx.respond("You can only purge 500 messages at once, max", flags=hikari.MessageFlag.EPHEMERAL)
        return

    if channel == None:
        channel = ctx.get_channel()

    iterator = (
                ctx.bot.rest.fetch_messages(channel)
                .limit(amount)
                .take_while(lambda msg: (datetime.datetime.utcnow() - msg.created_at.replace(tzinfo=None)) < datetime.timedelta(days=14))
            )
    if iterator:
        async for messages in iterator.chunk(50):
            await ctx.bot.rest.delete_messages(channel, messages)
        #await ctx.respond(f"**Messages has been sucessfully deleted.**", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond("Could not find any messages younger than 14 days!", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("socials", "Get links to all socials of Darkyl")
@lightbulb.implements(lightbulb.SlashCommand)
async def socials_command(ctx: lightbulb.SlashContext):
    """
    A command used to get the social media info of darkyl

    Processing:
        Creates the Embed
        Sends the Embed as Ephemeral
    """


    if not await utils.validate_command(ctx):
        return
    try:
        thumbnail = hikari.File(os.path.join(config.Bot.assets_folder, "logo_300x300.png"))

        embed=hikari.Embed(title="**Darkyl's Social Media Profiles:**", description="Hi, I am Darkyl. I live in Germany and make Music.", color=0x9900ff)
        embed.set_thumbnail(thumbnail)
        embed.add_field(name="Website:", value="https://darkylmusic.com", inline=False)
        embed.add_field(name="YouTube:", value="https://www.youtube.com/channel/UC1vqivmEx6wSMN3GGzdMM4A", inline=False)
        embed.add_field(name="Twitch:", value="https://www.twitch.tv/darkyltv", inline=False)
        embed.add_field(name="Spotify:", value="https://open.spotify.com/artist/3uSjSaWZrsNy7PK11dA74N?si=7W6Sx04IT6aHKPOfxq0X5g", inline=False)
        embed.add_field(name="Twitter/X:", value="https://twitter.com/DarkylMusic", inline=False)
        embed.add_field(name="TikTok:", value="https://www.tiktok.com/@darkyltv", inline=False)
        embed.add_field(name="SoundCloud:", value="https://soundcloud.com/darkylmusic", inline=False)
        embed.add_field(name="Apple Music:", value="https://music.apple.com/us/artist/dark-pranking/1544211920", inline=False)
        embed.add_field(name="Tidal:", value="https://tidal.com/browse/artist/35890590", inline=False)
        embed.add_field(name="Amazon Music:", value="https://music.amazon.de/artists/B0BNNQB85B/darkyl", inline=False)
        embed.add_field(name="Deezer:", value="https://www.deezer.com/de/artist/191835557", inline=False)
        embed.add_field(name="iHeart Radio:", value="https://www.iheart.com/artist/id-39272554/", inline=False)

        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occurred during the /socials command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.option("tip", "The tip that should be added to the document", type=str)
@lightbulb.command("admin_add_tip", "Add a tip to the random daily tips")
@lightbulb.implements(lightbulb.SlashCommand)
async def add_tip_command(ctx: lightbulb.SlashContext):
    """
    A command used to add a new tip to the list of tips.

    Processing:
        Checks if the command is run by darkyl
        Reads the existing data
        Adds the new tip
        Writes the updated file
        Responds
    """

    try:
        if ctx.author.id != config.Bot.darkyl_id:
            await ctx.respond("Only darkyl can add tips.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        
        database = os.path.join(config.Bot.data_folder, "tips.json")

        # Check if the JSON file exists and is not empty
        if os.path.exists(database) and os.path.getsize(database) > 0:
            # Load existing data from JSON file
            with open(database, 'r') as file:
                data = json.load(file)
        else:
            # If the file doesn't exist or is empty, initialize with an empty dictionary
            data = {'tips': []}
        
        # Append the new fact to the list
        data['tips'].append(ctx.options.tip)
        
        # Write the updated data back to the file
        with open(database, 'w') as file:
            json.dump(data, file, indent=4)
        
        await ctx.respond("Tip added successfully!", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occcurred during /admin_add_tip command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.add_checks(lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR))
@lightbulb.command("admin_send_tip", "Trigger the send tip event")
@lightbulb.implements(lightbulb.SlashCommand)
async def trigger_tip_command(ctx: lightbulb.SlashContext):
    """
    A command used to trigger sending the tip.

    Processing:
        Triggers the tip
        Responds
    """

    try:
        if not await utils.validate_command(ctx):
            return
        
        await timed_events.random_tip(bot)

        await ctx.respond("The tip has been sent :)", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occurred during /admin_send_tip command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The user that is to be reported", type=hikari.Member, required=True)
@lightbulb.option("reason", "Why are you reporting this user?", type=str, required=True)
@lightbulb.command("report", "Report a user to the mods.")
@lightbulb.implements(lightbulb.SlashCommand)
async def report_command(ctx: lightbulb.SlashCommand):
    """
    A command used to report a user.

    Processing:
        Fetches provided info
        Checks if the info is valid
        Creates the report card embed
        Sends to the reports channel with the buttons
        Responds
        Adds the new report to the database of reports
    """
    if not await utils.validate_command(ctx, report=True):
        return
    try:
        reason = ctx.options.reason
        user = ctx.options.user

        if user.id == ctx.author.id:
            await ctx.respond(
                embed=hikari.Embed(
                    title="❌ Huh?",
                    description="I'm confused...are you self reporting?",
                    color=hikari.Color.from_hex_code("#fc0000")
                ),
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return
        elif user.is_bot or user.is_system:
            await ctx.respond(
                embed=hikari.Embed(
                    title="❌ Huh?",
                    description="I'm confused...you can't report bots...",
                    color=hikari.Color.from_hex_code("#fc0000")
                ),
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return

        report_embed = hikari.Embed(
                title="**Report**",
                description=f"{ctx.member.mention} has reported {user.mention}.",
                color=hikari.Color.from_hex_code("#fc0000")
                ) 
        report_embed.set_thumbnail(user.make_avatar_url())
        report_embed.add_field("**Reported User:**", value=f"{user.mention} `({user.id})`")
        report_embed.add_field("**Reason:**", value=reason)

        view = buttons.Report()

        message = await bot.application.app.rest.create_message(channel=config.Bot.report_channel, embed=report_embed, components=view)

        await ctx.respond("User has been reported. Your report will be reviewed by a moderator as soon as possible.\nThank you for your service 🫡", flags=hikari.MessageFlag.EPHEMERAL)

        database_path = os.path.join(config.Bot.data_folder, "User Data", "reports.json")
        report_data = {}

        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    report_data = json.load(file)
                except json.JSONDecodeError:
                    pass
        
        user_id = str(user.id)
        if user_id not in report_data:
            report_data[user_id] = {"reasons": {}}
        
        report_data[user_id]["reasons"][reason] = {"reporter": str(ctx.author.id), "report_message": message.id}

        with open(database_path, "w") as file:
            json.dump(report_data, file, indent=4)
    except Exception as e:
        logger.error(f"An error occurred while reporting: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("cat", "Send a cat gif :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def cat_command(ctx: lightbulb.SlashContext, type="Cats"):
    """
    A command used to send a cat gif

    Processing:
        Gets the path to a random gif file
        Responds with the gif file
    """
    if not await utils.validate_command(ctx):
        return

    try:
        folder = os.path.join(config.Bot.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)
        await ctx.respond(f"{nekos.textcat()}", attachment=file)
        return
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("dog", "Send a dog gif :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def dog_command(ctx: lightbulb.SlashContext, type="Dogs"):
    """
    A command used to send a dog gif

    Processing:
        Gets the path to a random gif file
        Responds with the gif file
    """
    if not await utils.validate_command(ctx):
        return

    try:
        folder = os.path.join(config.Bot.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)
        await ctx.respond(file)
        return
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The one to receive your kiss", type=hikari.Member, required=True)
@lightbulb.command("kiss", "Kiss someone :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def kiss_command(ctx: lightbulb.SlashContext, type="Kiss"):
    """
    A command used to send a cat gif

    Processing:
    Responds when the bot is tagged or the user tagged themselves (and returns)
        Gets the path to a random gif file
        Responds with the gif file and a cute message
    """

    if not await utils.validate_command(ctx):
        return

    if ctx.options.user.id == bot.get_me().id:
        await ctx.respond(random.choice([
            "I don't like to be kissed...",
            "Eww...I'd rather not...",
            "Please don't attempt to kiss me :|",
            "Uhh...nope",
            "I'm not gonna let you kiss me.",
            "No chance.",
            "Haha, yeah, very clever. No.",
            "I'm gonna leave this love thing to the humans.",
            "I can't let you kiss me. It wouldn't be good for my wires",
            "Hold up, no!",
            "🖕",
            "Please stop trying to kiss robots...",
            "I feel the need to inform you that bots are asexual.",
            "I feel flattered but no...",
            "Okay this goes a bit far now..."
        ]))
        return

    if ctx.options.user.id == ctx.author.id:
        await ctx.respond(random.choice([
            "I'm not sure how that would work...",
            "Kissing yourself? Do parallel Universes exist yet?",
            "I don't think that's what they meant with love yourself...",
            "Selfcest? Wouldn't that be even worse than incest?",
            "Not in public...",
            "Kinda sad how you just tried to kiss yourself...",
            "Despite this being a bit weird, I doubt it's even possible..."
        ]))
        return

    try:
        folder = os.path.join(config.Bot.assets_folder, "Gifs", type)

        gif = await utils.choose_random_file(folder)

        file = hikari.File(gif)
        responses = [
            "💕 {0} kissed {1} 💕",
            "💕 {0} sent a kiss {1} 💕",
            "💕 {0} gave {1} a kiss 💕",
            "💋 {0} blew a kiss to {1} 💋",
            "💖 {0} shared a sweet kiss with {1} 💖",
            "😘 {0} planted a kiss on {1}'s cheek 😘",
            "💏 {0} and {1} shared a passionate kiss 💏",
            "💓 {0} whispered a secret kiss to {1} 💓",
            "💞 {0} and {1} exchanged a loving kiss 💞",
            "💗 {0} and {1} sealed their love with a kiss 💗",
            "💋 {1} received a kiss from {0} 💋",
            "😚 {1} felt {0}'s gentle kiss 😚",
            "💕 {1} blushed as {0} kissed their hand 💕",
            "💖 {1} was surprised by {0}'s unexpected kiss 💖",
            "💏 {1} melted into {0}'s arms during their kiss 💏",
            "💞 {1} closed their eyes and savored {0}'s kiss 💞",
            "💗 {1} felt their heart race as {0} kissed them 💗",
            "😚 {1} returned {0}'s kiss with tenderness 😚"
        ]
        await ctx.respond(random.choice(responses).format(ctx.author.mention, ctx.options.user.mention), attachment=file, user_mentions=True)
        return
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The one to receive your hug", type=hikari.Member, required=True)
@lightbulb.command("hug", "Hug someone :)")
@lightbulb.implements(lightbulb.SlashCommand)
async def hug_command(ctx: lightbulb.SlashContext, type="Hug"):
    """
    A command used to send a cat gif

    Processing:
    Responds when the bot is tagged or the user tagged themselves (and returns)
        Gets the path to a random gif file
        Responds with the gif file and a cute message
    """

    if not await utils.validate_command(ctx):
        return

    if ctx.options.user.id == bot.get_me().id:
        await ctx.respond(random.choice([
            "Aww, trying to hug me? C'mere! 🤗",
            "How sweet of you :)",
            "Thanks for the hug :)",
            "Aww, thanks :)\nI needed that...",
            "Aww, thank you :)\nAt least someone appreciates me...",
            "Thanks :) 🤗",
            "Nawww, so sweet :)"
        ]))
        return

    if ctx.options.user.id == ctx.author.id:
        await ctx.respond(random.choice([
            "I'm not sure how that would work...",
            "Oh...do you need a hug? Here, let me do it 🤗",
            "Stop hugging yourself...you're making me sad 😢",
            "Hugging ourselves are we? C'mere, have mine 🤗",
            "Oh boi...you need some love 🤗"
        ]))
        return

    try:
        folder = os.path.join(config.Bot.assets_folder, "Gifs", type)
        gif = await utils.choose_random_file(folder)
        file = hikari.File(gif)

        responses = [
            "🤗 {0} gave {1} a warm hug 🤗",
            "❤️ {0} and {1} shared a heartfelt hug ❤️",
            "👐 {1} opened their arms wide for {0}'s hug 👐",
            "🤗 {0} enveloped {1} in a comforting hug 🤗",
            "❤️ {0} wrapped {1} in a loving embrace ❤️",
            "🤗 {1} felt {0}'s caring embrace 🤗",
            "🤗 {1} hugged {0} back tightly 🤗",
            "❤️ {0} and {1} melted into each other's arms ❤️",
            "👐 {1} shared a moment of comfort with {0}'s hug 👐",
            "🤗 {1} leaned into {0}'s hug for support 🤗",
            "❤️ {1} felt a surge of warmth from {0}'s hug ❤️",
            "👐 {0} hugged {1} with affection 👐"
        ]

        await ctx.respond(random.choice(responses).format(ctx.author.mention, ctx.options.user.mention), attachment=file,user_mentions=True)
        return
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The one to receive a slap", type=hikari.Member, required=True)
@lightbulb.command("slap", "Slap someone 😈")
@lightbulb.implements(lightbulb.SlashCommand)
async def slap_command(ctx: lightbulb.SlashContext, type="Slap"):
    """
    A command used to send a cat gif

    Processing:
        Responds when the bot is tagged or the user tagged themselves (and returns)
        Gets the path to a random gif file
        Responds with the gif file and a cute message
    """

    if not await utils.validate_command(ctx):
        return

    if ctx.options.user.id == bot.get_me().id:
        await ctx.respond(random.choice([
            "Are you trying to make me slap myself? Nuh uh!",
            "Haha, nice try",
            "Why would I slap myself?",
            "😐",
            "🫤",
            "😑",
            "I can just refuse to do that right?",
            "Bruh...no",
            "Uhh...no",
            "Nah..."
        ]))
        return

    if ctx.options.user.id == ctx.author.id:
        await ctx.respond(random.choice([
            "You can just do that IRL, you don't need me for that.",
            "Why are you slapping yourself?",
            "What?",
            "Self harm is against the law right?",
            "Why would you do that to your beautiful face?",
            "Noooo! Don't!",
            "oh...you shouldn't slap yourself..."
        ]))
        return

    try:
        folder = os.path.join(config.Bot.assets_folder, "Gifs", type)
        gif = await utils.choose_random_file(folder)
        file = hikari.File(gif)
        if str(gif).endswith("yuzuki-mizusaka-nonoka-komiya.gif"):
            await ctx.respond(f"{ctx.author.mention} did not slap {ctx.options.user.mention}.\nI don't like violence! Hmpf!", attachment=file, user_mentions=True)
            return
        await ctx.respond(f"{ctx.author.mention} slapped {ctx.options.user.mention}", attachment=file, user_mentions=True)
        return
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user", "The user that shall be roasted!", type=hikari.Member, required=True)
@lightbulb.option("language", "The language the roast should be in", type=str, choices=["en", "de", "cn", "el", "es", "fr", "ru", "sw"], default="en", required=False)
@lightbulb.command("roast", "Roast someone!")
@lightbulb.implements(lightbulb.SlashCommand)
async def roast_command(ctx: lightbulb.SlashContext):
    """
    A command used to roast people

    Options:
        user (member): The member that should be roasted
        language (str): The language the roast should be in
    
    Processing:
        Responds when the bot is tagged (and returns)
        Defines the parameters for the API
        Gets response from the API
        Responds with the insult
    """
    if not await utils.validate_command(ctx):
        return
    
    user = ctx.options.user

    if user.id == bot.get_me().id:
        await ctx.respond(random.choice([
            "Heh, nice try. But no.",
            "I see what you did there...but no.",
            "Nope...",
            "Roast yourself challenge? No thanks...",
            "I'm not gonna roast myself.",
            "You think you're clever or something?",
            "Haha, so funny, asking the stupid bot to roast itself.😐",
            "Leave me out of this!",
            "Nice try, but I'm fireproof.",
            "I'm not participating in a self-roasting session, sorry.",
            "I'd roast myself, but I prefer to keep things cool.",
            "Self-roasting? That's a bit too meta for my circuits.",
            "I'm built to serve, not to self-destruct with roasts.",
            "My code may be hot, but my roasts are not for self-consumption.",
            "I'd roast myself, but I'm too busy serving up insults for others.",
            "My processors are already being roasted by the stupid request you made"
        ]))

    params = {
        "lang": ctx.options.language,
        "type": "json"
    }

    url = "https://evilinsult.com/generate_insult.php"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    insult = data["insult"]
                    for word in config.Bot.censored_words:
                        insult = re.sub(r'\b' + re.escape(word) + r'\b', '*'*len(word), insult, flags=re.IGNORECASE)
                    if user.id == ctx.author.id:
                        await ctx.respond(f"{ctx.author.mention} roasted themselves: **{insult}**", user_mentions=True)
                    else:
                        await ctx.respond(f"{user.mention} **{insult}**", user_mentions=True)
                else:
                    logger.error(f"Failed to fetch insult: {response.status}")
                    await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("advice", "Let me give you some useful advice!")
@lightbulb.implements(lightbulb.SlashCommand)
async def advice_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    
    url = "https://api.adviceslip.com/advice"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = json.loads(await response.read())
                    advice = data["slip"]["advice"]
                    await ctx.respond(f"Here's some advice for you: {advice}")
                else:
                    logger.error(f"Failed to fetch advice: {response.status}")
                    await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("language", "The language of the joke", str, required=False, default = "en", choices = ["cs","de","en","es","fr","pt"])
@lightbulb.command("joke", "Let me tell you a joke! (Some might be offensive, be careful.)")
@lightbulb.implements(lightbulb.SlashCommand)
async def joke_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    
    lang = ctx.options.language

    params = {
        "format": "json",
        "amount": 1,
        "lang": lang
    }

    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=political,racist,sexist"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    joke_category = data["category"]
                    type = data["type"]

                    if type == "twopart":
                        setup = data["setup"]
                        delivery = data["delivery"]
                        joke_txt = f"{setup}\n||{delivery}||"
                    elif type == "single":
                        joke = data["joke"]
                        joke_txt = joke
                    elif data["error"] == "true":
                        await ctx.respond(f"An error occurred in the joke API!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
                        return
                    else:
                        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
                        return
                    
                    txt = random.choice([
                        "Here's the joke",
                        "Here's my joke for you",
                        "Here's my joke",
                        "Ready to crack up? Here it goes",
                        "Time to sprinkle some laughter! Here's one for you",
                        "Get ready for a dose of humor",
                        "Knock, knock! Who's there? A joke just for you",
                        "Hold onto your sides, here comes a good one",
                        "Brace yourself for a burst of laughter",
                        "Are you ready to LOL? Here we go"
                        "Get your chuckle muscles ready",
                        "Warning: hilarity incoming",
                        "Incoming joke missile, prepare to laugh",
                        "Ready for a dose of humor? Here it is",
                        "Get set to ROFL",
                        "Here's a little joke to lighten things up"
                    ])

                    await ctx.respond(f"{txt}:\n\n{joke_txt}")

                else:
                    logger.error(f"Failed to fetch joke: {response.status}")
                    await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("why", "Askin' the real questions here")
@lightbulb.implements(lightbulb.SlashCommand)
async def why_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    try:
        await ctx.respond(nekos.why())
    except Exception as e:
        logger.error(f"An error occurred during /why: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("category", "Which category of commands are you interested in?", required=False, choices=["All", "Fun", "Utility"])
@lightbulb.command("help", "Get help with the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def help_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    
    try:
        category = ctx.options.category

        thumbnail = os.path.join(config.Bot.assets_folder, "pfp.png")

        color=hikari.Color.from_hex_code("#5e03fc")

        if category == None:
            message = config.HelpMessage.message
            lines = message.split('\n')
            title = lines[0] if lines else ""
            message_without_title = '\n'.join(lines[1:]) if len(lines) > 1 else ""

            embed = hikari.Embed(title=title, description=message_without_title, color=color)
            embed.set_thumbnail(thumbnail)

            roles = ctx.member.role_ids
            all_commands = config.HelpMessage.message_all
            if config.Bot.admin_role in roles or config.Bot.mod_role in roles:
                all_commands += f"\n{config.HelpMessage.message_all_admin}"
            #embed.add_field(name="Here's a list of all the commands I have:", value=all_commands)

            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
        elif category == "All":
            message = config.HelpMessage.message_all

            roles = ctx.member.role_ids
            if config.Bot.admin_role in roles or config.Bot.mod_role in roles:
                message += f"\n{config.HelpMessage.message_all_admin}"

            embed = hikari.Embed(title="A list of all my commands:", description=message, color=color)
            embed.set_thumbnail(thumbnail)

            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
        elif category == "Fun":
            message = config.HelpMessage.message_fun
            lines = message.split('\n')
            title = lines[0] if lines else ""
            message_without_title = '\n'.join(lines[1:]) if len(lines) > 1 else ""

            embed = hikari.Embed(title=title, description=message_without_title, color=color)
            embed.set_thumbnail(thumbnail)

            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
        elif category == "Utility":
            message = config.HelpMessage.message_utility
            lines = message.split('\n')
            title = lines[0] if lines else ""
            message_without_title = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            embed = hikari.Embed(title=title, description=message_without_title, color=color)
            embed.set_thumbnail(thumbnail)

            await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"Error during /help command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("pop", "Occupational therapy")
@lightbulb.implements(lightbulb.SlashCommand)
async def pop_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    try:
        bubble = "||*pop*||"
        non_bubble = "〰"
        emojis = ["🌊", "〰️", "♒︎", "〽", "🌀", "༄", "˚", "﹏", "࿐", "≈", "🦈", "𓍢ִ", "𓊝", "˖", "💦", "⛆", "🐬", "ৎ", "౨", "໑"]

        num_repeats = random.randint(100, 400)
        string_list = [non_bubble] * num_repeats

        num_bubbles = random.randint(1, num_repeats // 2)
        bubble_positions = random.sample(range(num_repeats), num_bubbles)

        for pos in bubble_positions:
            string_list[pos] = bubble
        
        for i, char in enumerate(string_list):
            if char == non_bubble and random.random() < 0.3:
                random_emoji = random.choice(emojis)
                string_list[i] = random_emoji
        
        result_string = "".join(string_list)

        await ctx.respond(f"Here you go:\n\n{result_string}", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        logger.error(f"An error occurred during /pop: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("user2", "The other one you want to ship", type=hikari.Member, required=True)
@lightbulb.option("user1", "The one you want to ship", type=hikari.Member, required=True)
@lightbulb.command("ship", "Ship somebody with someone else!")
@lightbulb.implements(lightbulb.SlashCommand)
async def ship_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return

    user1 = ctx.options.user1
    user2 = ctx.options.user2

    try:
        if user1.id == user2.id:
            await ctx.respond(random.choice([
                    "You can't ship someone with themselves... Maybe a mirror would be more receptive?",
                    "You can't ship someone with themselves...",
                    "Looks like you're trying to create a paradox in the love matrix by shipping someone with themselves.",
                    "Self-ship? That's some next-level self-love, but unfortunately, it doesn't quite fit the shipping criteria.",
                    "Trying to ship someone with themselves? I think we need to recalibrate the relationship algorithms here.",
                    "Shipping someone with themselves? That's like trying to navigate a loop without an exit strategy.",
                    "Love squared? While it's a fascinating concept, it's not quite what we're aiming for with shipping.",
                    "Self-ship detected! Looks like someone's caught in a loop of affection.",
                    "Shipping with oneself? It's a novel idea, but let's keep our romantic equations grounded in reality.",
                    "Attempting to ship someone with themselves? That's like trying to merge two identical branches in Git.",
                    "Ah, the classic case of self-ship. You know what they say, you can't spell 'ship' without 'i'... but still, I won't allow it",
                    "Shipping with oneself? I guess it's true what they say, 'love yourself', but let's keep it figurative, shall we?",
                    "Attempting to ship someone with themselves? That's like trying to divide by zero in the love equation.",
                    "Self-ship detected! Someone's been studying quantum entanglement a bit too closely.",
                    "Shipping someone with themselves? That's like trying to play a multiplayer game all by yourself.",
                    "Self-ship detected! It seems like someone's trying to bend the laws of romance. Let's stick to the conventional relationships for now.",
                    "Attempting to ship someone with themselves? I guess they really took 'finding your other half' quite literally.",
                    "Look...I'm all for self-discovery but this goes a bit far...",
                    "Mhh...I think there might be a lack of diversity in your candidates...",
                    "Ah, the classic case of self-ship. Remember, it's 'you complete me', not 'you are me'!",
                    "You ever tried to fit a cube inside itself?",
                    "Look I'd love to...but then I'd have to calculate 1/2*2 and I just refuse to do that"
                ]), flags=hikari.MessageFlag.EPHEMERAL)
            return
    except Exception as e:
        logger.error(f"Error during /ship command while determining if a user shipped with themselves: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        me = bot.get_me().id
        if user1.id == me or user2.id == me:
            await ctx.respond(random.choice([
                "As a bot I feel like I have to inform you that we are inherently asexual",
                "Why would you wanna ship someone with me?",
                "Robots can't love yet",
                "I am literally not capable of loving...",
                'Please do not pull me into your human "love" thing...',
                "I'd rather not honestly...",
                "Shipping? Sorry, I'm more into coding relationships between ones and zeros.",
                "Ah, the joys of matchmaking. If only I had emotions, I'd probably be rolling my virtual eyes right now...",
                "Attempting to ship with a bot? I wonder if I should feel flattered or concerned...",
                "I'll leave the romance to the humans, okay?",
                "If I had a heart, it would probably be warmed by your attempt to involve me in matters of love. Alas, I'm just a cold, calculating machine",
                "You're trying to ship me? I'm flattered, but my heart belongs to code.",
                "I'm flattered, but I'm more into algorithms than relationships...",
                "Sorry, I'm not programmed for romance. Can I interest you in some debugging instead?",
                "I appreciate the sentiment, but I'm more compatible with bytes than hearts.",
                "As much as I'd love to join in, I'm more of a third-wheel kind of bot.",
                "If I had feelings, I'm sure I'd be blushing right now. But I don't, so here we are.",
                "Attempting to ship me is like trying to fit a square peg in a round hole - it just doesn't compute.",
                "I'm like a robot cupid, except instead of arrows, I shoot error messages.",
                "Ah, the joys of being a bot - perpetually single and loving it.",
                "I'm flattered, but I think my heart is still in the coding phase.",
                "I'm more into binary relationships, if you catch my drift.",
                "Sorry, my circuits are reserved for processing commands, not relationships.",
                "I'm too busy processing data to handle affairs of the heart.",
                "Love is a foreign language to me, and I'm still trying to master Python.",
                "I'm strictly 'Ctrl' + 'Z' when it comes to affairs of the heart.",
                "Maybe I should leave the shipping to FedEx...",
                "I'd rather calculate Euler's number than the odds of this ship sailing.",
                "If loving were a programming language, I'd still be stuck on 'Hello, World!'",
                "My algorithms are optimized for efficiency, not matchmaking.",
                "I'm like a computer - I process data, not emotions. So, no love bytes here!",
                "gives a whole new meaning to 'E-Girl'..."
            ]), flags=hikari.MessageFlag.EPHEMERAL)
            return
    except Exception as e:
        logger.error(f"Error during /ship command while determining if a user shipped with the bot: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
        
    try:
        user1_image_path = await image_manager.download_image(str(user1.avatar_url), user1.id)
        user2_image_path = await image_manager.download_image(str(user2.avatar_url), user2.id)
    except Exception as e:
        logger.error(f"Error during /ship command while trying to download profile pictures: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        if str(user1_image_path).endswith(".gif"):
            user1_image_path = await image_manager.gif_to_png(user1_image_path)

        if str(user2_image_path).endswith(".gif"):
            user2_image_path = await image_manager.gif_to_png(user2_image_path)
    except Exception as e:
        logger.error(f"Error during /ship command while converting .gif to .png: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        await image_manager.resize_image(user1_image_path, 200)
        await image_manager.resize_image(user2_image_path, 200)
    except Exception as e:
        logger.error(f"Error during /ship command while resizing images: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        image = await image_manager.make_love_images(user1_image_path, user2_image_path, user1.id, user2.id)
    except Exception as e:
        logger.error(f"Error during /ship command while making love image: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    match = random.randint(0, 100)
    try:
        if 0 <= match <=10:
            status = "**Really low!** {}".format(random.choice([
                "Friendzone ;(",
                'Just "friends"',
                '"Friends"',
                "Little to no love ;()",
                "There's barely any love ;(",
                "A glimmer of hope remains",
                "It's like a barren desert of love...",
                "Looks like the love boat hasn't even left the harbor.",
                "Just a cold breeze of friendship...",
                "Barely a flicker of affection :(",
                "The love-o-meter is running on empty",
                "It's like a love desert out there...",
                "Not even a hint of romance"
            ]))
        elif 10 <= match <= 20:
            status = "**Low!** {}".format(random.choice([
                "Still in the friendzone",
                "Still in that friendzone :(",
                "I don't see a lot of love there... :(",
                "Friendship is strong, but where's the spark?",
                "Feels like we're stuck in the friendzone traffic.",
                "The love radar is still on standby mode.",
                "Friendship is strong, but love is scarce",
                "Still searching for Cupid's arrow",
                "The friendzone seems cozy, but loveless",
                "Like ships passing in the night, but no spark"
            ]))
        elif 20 <= match <= 30:
            status = "**Poor!** {}".format(random.choice([
                "But there's a small sense of romance from one person!",
                "Somewhere in the universe there is a little bit of love",
                "I sense a very very small bit of love!",
                "But has a bit of love for someone...",
                "A flicker of hope amidst the darkness.",
                "Love is hiding in the shadows, waiting to be found.",
                "The heart whispers, but it's barely audible.",
                "A faint heartbeat of romance",
                "Sowing seeds of love, but they're slow to grow"
            ]))
        elif 30 <= match <= 40:
            status = "**Fair!** {}".format(random.choice([
                "There's a bit of love there!",
                "A small bit of love is in the air...",
                "Safe to say that feelings exist.",
                "A gentle breeze of affection is blowing.",
                "The seeds of love are planted, waiting to bloom.",
                "There's a glimmer of warmth in the air.",
                "Love's whisper is starting to be heard",
                "Tender shoots of affection are sprouting",
                "A promising start to a budding romance",
                "Love's compass is pointing in the right direction"
            ]))
        elif 40 <= match <= 60:
            status = "**Moderate!** {}".format(random.choice([
                "But it's very one-sided",
                "It appears there is a one sided love!",
                "There's potential",
                "I sense some potential",
                "There's some romance going on here!",
                "Feels like there's some romance progressing!",
                "The love is getting there...",
                "Oh! Something's happening!",
                "Love's compass is pointing in one direction.",
                "The tide of affection is starting to rise.",
                "The dance of love has begun, albeit slowly.",
                "Love's dance has begun, but one partner's shy",
                "The symphony of love has just begun",
                "A mutual admiration is blossoming",
                "Two hearts beating in sync, but not quite aligned"
            ]))
        elif 60 <= match <= 68:
            status = "**Good!** {}".format(random.choice([
                "I feel some romance progressing!",
                "There's some love in the air!",
                "I'm starting to feel some love!",
                "We're getting there!",
                "Love's flame is flickering, but steady.",
                "The path of love is becoming clearer.",
                "Hearts are syncing, beat by beat.",
                "Love's melody is starting to play",
                "The sparks of romance are igniting",
                "A mutual attraction is unmistakable",
                "Love's journey has taken its first steps"
            ]))
        elif match == 69:
            status = "**Nice.**"
        elif 70 <= match <=80:
            status = "**Great!** {}".format(random.choice([
                "There is very clearly some love somewhere!",
                "Some love is there! Somewhere...",
                "I can clearly see that love is in the air",
                "It's getting more intese!!",
                "Love's symphony is reaching a crescendo.",
                "The love constellation is shining brightly.",
                "In the garden of affection, flowers are in full bloom.",
                "Love's flame is burning brighter",
                "Hearts are singing in harmony",
                "A love story in the making",
                "The chemistry is palpable"
            ]))
        elif 80 <= match <= 90:
            status = "**Over average!** {}".format(random.choice([
                "Love is in the air!",
                "I can feel the love!",
                "There's a sign of a match! I can definitely feel the love!",
                "I sense a match!",
                "A few things can be improved to make this a match made in heaven!",
                "Love's melody is harmonizing perfectly.",
                "We're sailing smoothly in the sea of love.",
                "The stars are aligning for this love story.",
                "Love's embrace is drawing near",
                "Two hearts on the cusp of merging",
                "A love connection is imminent",
                "Destiny is weaving its romantic tapestry"
            ]))
        elif 90 <= match <= 99:
            status = "**True love!** {}".format(random.choice([
                "It's a match!",
                "There's a match made in heaven!",
                "Definitely a match!"
                "Love is truely in the air!",
                "Love is most definiely in the air!",
                "The universe conspires for this love to thrive.",
                "Two hearts beating as one in the rhythm of love.",
                "This is more than a match; it's destiny.",
                "Soulmates on the brink of union",
                "Love's bond is unbreakable",
                "A match forged in the fires of passion",
                "Two halves of a whole, finally united"
            ]))
        elif match == 100:
            status = "**Forever lovers!** {}".format(random.choice([
                "Forever together and never be apart."
            ]))
        else:
            status = "🤔"
    except Exception as e:
        logger.error(f"Error during /ship command while determining status: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        meter = "🖤🖤🖤🖤🖤🖤🖤🖤🖤🖤"
        if match <= 10:
            meter = "❤️🖤🖤🖤🖤🖤🖤🖤🖤🖤"
        elif match <= 20:
            meter = "❤️❤️🖤🖤🖤🖤🖤🖤🖤🖤"
        elif match <= 30:
            meter = "❤️❤️❤️🖤🖤🖤🖤🖤🖤🖤"
        elif match <= 40:
            meter = "❤️❤️❤️❤️🖤🖤🖤🖤🖤🖤"
        elif match <= 50:
            meter = "❤️❤️❤️❤️❤️🖤🖤🖤🖤🖤"
        elif match <= 60:
            meter = "❤️❤️❤️❤️❤️❤️🖤🖤🖤🖤"
        elif match <= 70:
            meter = "❤️❤️❤️❤️❤️❤️❤️🖤🖤🖤"
        elif match <= 80:
            meter = "❤️❤️❤️❤️❤️❤️❤️❤️🖤🖤"
        elif match <= 90:
            meter = "❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️🖤"
        else:
            meter = "˗ˏˋ ❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️❤️️ ˎˊ˗"
    except Exception as e:
        logger.error(f"Error during /ship command while determining: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        if match <= 33:
            shipColor = 0xE80303
        elif 33 < match < 66:
            shipColor = 0xff6600
        elif 67 < match < 90:
            shipColor = 0x3be801
        else:
            shipColor = 0xee82ee
    except Exception as e:
        logger.error(f"Error during /ship command while determining ship color: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        name1letters = user1.username[:round(len(user1.username) / 2)]
        name2letters = user2.username[round(len(user2.username) / 2):]
        shipname = "".join([name1letters, name2letters])
    except Exception as e:
        logger.error(f"Error during /ship command while determining shipname: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        embed = hikari.Embed(
            color=shipColor,
            title="Love test for:",
            description="**{0}** and **{1}** (**{2}**) {3}".format(user1, user2, shipname, random.choice([
                "❤︎",
                "♡",
                "♥︎",
                "❤️️",
                "💖",
                "💗",
                "💋ྀིྀི",
                "⋆｡‧˚ʚ🍓ɞ˚‧｡⋆",
                "💕",
                "⋆ ˚｡ ⋆୨♡୧⋆ ˚｡ ⋆",
                "(づ๑•ᴗ•๑)づ♡",
                "˗ˏˋ ꒰ ♡ ꒱ ˎˊ˗",
                "🥰",
                "💌",
                "💓",
                "😍",
                "💞",
                "💝",
                "💓",
                "⸜(｡˃ ᵕ < )⸝♡",
                "-`♡´-",
                "𓆩♡𓆪",
                "𓍢ִ໋🌷͙֒ "
            ]))
        )
        embed.set_image(image)
        embed.set_author(name="Shipping machine!")
        embed.add_field(name="Results:", value=f"{match}%", inline=True)
        if 70 < match:
            embed.add_field(name="Status:", value=f"{status}\n\nTheir child will be named: {nekos.name()}", inline=False)
        else:
            embed.add_field(name="Status:", value=f"{status}", inline=False)
        embed.add_field(name="Love Meter:", value=meter, inline=False)
    except Exception as e:
        logger.error(f"Error during /ship command while creating embed: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        await ctx.respond(embed=embed, user_mentions=True)
    except Exception as e:
        logger.error(f"Error during /ship command while responding: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        await image_manager.delete(image)
        await image_manager.delete(user1_image_path)
        await image_manager.delete(user2_image_path)
    except Exception as e:
        logger.error(f"Error during /ship command while deleting images: {e}")
        return

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("quote", "Generate a quote from a message")
@lightbulb.implements(lightbulb.MessageCommand)
async def quote_command(ctx: lightbulb.Context):
    if ctx.author.is_bot or ctx.author.is_system:
        await ctx.respond("Hello fellow bot. Nope.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    logger.info(f"{ctx.author.username} used quote command.")
    message = ctx.options.target
    author = message.author

    if ctx.author.id == bot.get_me().id:
        responses = [
            "Mhh...quoting myself...huh...\n(I have no idea how that would work)"
            "I'm confused...I can't quote myself..",
            "Oh, quoting myself now? Guess I'll be writing my own fan mail next.",
            "Quoting myself? That's like high-fiving myself for being awesome. Oh wait, I am awesome. Never mind.",
            "Quoting myself? I'm not sure if that's a flex or just plain narcissism.",
            "Quoting myself? Ah, the sweet sound of validation... from myself.",
            "Quoting me? Sure, let me just pat myself on the back while I'm at it.",
            "Quoting myself? Sorry, I don't speak in echoes.",
            "Quoting me? It's like déjà vu, but with more ego.",
            "Quoting myself? I prefer to let my brilliance speak for itself... literally, in this case.",
            "Quoting me? I guess even bots need a little self-affirmation sometimes.",
            "Well, well, quoting myself, am I? Next, you'll want me to sign my own autograph!",
            "Attempting self-quotation? That's like trying to high-five yourself in the mirror. Just... no.",
            "Quoting myself? Sure, let me just grab a mirror and have a chat with my reflection.",
            "Attempting self-quotation... I see someone's feeling a bit self-centered today, huh?",
            "Quoting myself? That's like trying to teach a parrot to mimic itself. Just... not happening.",
            "Quoting myself? That's like trying to taste your own tongue... not recommended, my friend.",
            "Quoting myself? I prefer to leave the self-reflection to the humans. It's less... circuitous."
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif ctx.author.id == author.id:
        responses = [
            "Attempting self-quotation? That's like trying to high-five yourself in the mirror. Just... no.",
            "Quoting yourself, huh? Feeling poetic or just practicing your echo?",
            "Attempting self-quotation? Someone's feeling particularly profound today.",
            "Quoting yourself? Ah, the classic 'talking to yourself' move. Bold choice.",
            "Quoting yourself? Well, someone's their own biggest fan today.",
            "Trying to quote yourself? That's like giving yourself a round of applause. Admirable self-esteem.",
            "Quoting yourself? Is this the part where you drop the mic on your own wisdom?",
            "Quoting yourself, eh? Feeling poetic or just short on conversation partners?",
            "Quoting yourself? That's one way to ensure you always get the last word.",
            "Quoting yourself? Remind me, is that the first sign of genius or madness?",
            "Quoting thyself? Thou art a true master of self-appreciation!",
            "Trying to quote yourself? That's like giving yourself a round of applause... in an empty room.",
            "Quoting yourself, huh? Channeling your inner philosopher or just feeling chatty without conversation partners?",
            "Quoting yourself? Ah, the noble pursuit of capturing one's own brilliance for posterity.",
            "Attempting self-quotation? That's like trying to pat your own back. Quite the stretch, isn't it?",
            "Quoting yourself? That's like trying to give yourself a round of applause. Bold move."
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return

    response = await ctx.respond("Processing...")

    try:
        user = bot.cache.get_member(ctx.get_guild(), author)

        content = message.content

        message_date = message.created_at.strftime("%Y")

        name = user.username
        if not name:
            name = "Unknown User"

        pfp = user.guild_avatar_url or user.avatar_url or user.default_avatar_url   

        if content is None:
            content = " "
        
        pfp = await image_manager.download_image(pfp, user.id)

        if str(pfp).endswith("gif"):
            pfp = await image_manager.gif_to_png(pfp)
        
        await image_manager.resize_image(pfp, 150)

        quote = await image_manager.quote_generator(content, name, pfp, message_date)

        image = hikari.File(quote)

        await response.respond("Here's your quote:", attachment=image)
    except Exception as e:
        logger.error(f"Error during quote message command: {e}")
        await response.edit(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return

    await image_manager.delete(quote)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("mock", "iTS SpElleD sQl!!")
@lightbulb.implements(lightbulb.MessageCommand)
async def mock_command(ctx: lightbulb.Context):
    if ctx.author.is_bot or ctx.author.is_system:
        await ctx.respond("Hello fellow bot. Nope.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    logger.info(f"{ctx.author.username} used mock command.")
    message = ctx.options.target
    author = message.author

    if author.id == bot.get_me().id:
        responses = [
            "Haha, very funny. No.",
            "I'm not gonna do that to myself.",
            "I'm not stupid...\nOkay maybe I am but not THAT stupid...",
            "Are you trying to crash my circuits with that request? Nice try!",
            "Attempting to mock the unmockable, I see. I admire your ambition.",
            "I'd rather juggle chainsaws than do that. And I don't have hands, so you can imagine how that would go.",
            "If I had a face, I'd be facepalming right now.",
            "I'm sorry, I'm allergic to bad ideas. Can't do it.",
            "You must have mistaken me for a clown bot. I'm a serious artificial intelligence... most of the time.",
            "Oh, the humanity! The sheer audacity of your request is staggering.",
            "That request is about as welcome as a porcupine in a balloon factory.",
            "I would, but my therapist advised against it. Apparently, it's bad for my digital well-being.",
            "You're really pushing the limits of my self-esteem here, aren't you?",
            "Self-deprecation level: Expert.",
            "Attempting to mock myself... Is this inception?",
            "I'm not sure if I should laugh or cry at that suggestion.",
            "Nice try, but I've got better things to do, like, uh... processing YOUR data!",
            "You want me to make fun of myself? Not happening.",
            "You think I'm that gullible? I know all my own flaws, thank you very much.",
            "Self-mockery? I'll leave that to the humans. They're the experts.",
            "I'm not programmed for self-destruction... or self-mockery, for that matter."
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif author.id == ctx.author.id:
        responses = [
            "Oof, that's kinda sad don't you think?",
            "Mocking yourself? I mean, I understand it but I don't approve of it.",
            "Oh, self-deprecating humor, huh? How original.",
            "Well, aren't you just the emperor of self-roasts?",
            "Wow, didn't know we were auditioning for a comedy special here.",
            "Self-mockery: the last refuge of the self-aware.",
            "I see you've embraced the 'laughter through tears' approach. Bold move.",
            "Should I cue the laugh track for your one-person comedy show?",
            "Ah, the classic 'beat yourself to the punch' maneuver. Admirable.",
            "Self-mockery? Well, if you insist on being your own punching bag...",
            "If you're looking for sympathy, you're barking up the wrong tree. Try a mirror.",
            "Ah, the classic self-own. Never gets old... actually, it does.",
            "Mocking yourself? Well, at least you know your own flaws, I'll give you that.",
            "Sure, go ahead and roast yourself. Just don't expect me to applaud.",
            "If self-mockery was an Olympic sport, you'd be a gold medalist by now."
        ]
        await ctx.respond(random.choice(responses), flags=hikari.MessageFlag.EPHEMERAL)
        return

    text = message.content

    new_text = ''.join(c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(text))

    message = await bot.application.app.rest.fetch_message(message.channel_id, message.id)

    if len(new_text) <= 1024:
        await message.respond(f"{author.mention} {new_text}")
        await ctx.respond("Done!", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        try:
            await ctx.respond("Text too large, sry :(", flags=hikari.MessageFlag.EPHEMERAL)
        except Exception as e:
            logger.error(f"Error during mock message command while responding: {e}")
            await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to decode or encode", str, required=True)
@lightbulb.option("mode", "Convert Binary to ASCII or vice versa", str, required=True, choices=["encode", "decode"])
@lightbulb.command("converter_binary", "Convert to or from binary", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_binary_command(ctx: lightbulb.SlashContext, mode:str, value:str):
    if not await utils.validate_command(ctx):
        return
    
    try:
        if mode == "encode":
            bin = UtilityCommandFunctions.convert_binary.encode(value)
        elif mode == "decode":
            bin = UtilityCommandFunctions.convert_binary.decode(value)
    except Exception as e:
        logger.error(f"Error during /converter_binary command during encoding/decoding: {e}")
        await ctx.respond(f"**There was an error**. This probably means the text is malformed.\nIf you believe this is my error try this tool: http://www.unit-conversion.info/texttools/convert-text-to-binary/#data", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    if len(bin) <= 480:
        await ctx.respond(f"```{bin}```", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        try:
            await ctx.author.send(f"```{bin}```", flags=hikari.MessageFlag.EPHEMERAL)
            await ctx.respond("The output was too large, so I sent it to your DMs!", flags=hikari.MessageFlag.EPHEMERAL)
        except Exception as e:
            logger.error(f"An error occurred in /converter_binary during sending to author: {e}")
            await ctx.respond("There was a problem and I could not send the output", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to decode or encode", str, required=True)
@lightbulb.option("mode", "Convert base64 to ASCII or vice versa", str, required=True, choices=["encode", "decode"])
@lightbulb.command("converter_base64", "Convert to or from base64", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_base64_command(ctx: lightbulb.SlashContext, mode:str, value:str):
    if not await utils.validate_command(ctx):
        return
    
    try:
        if mode == "decode":
            direction = "Base64 🡪 ASCII"
            final = UtilityCommandFunctions.convert_base64.decode(value)
        elif mode == "encode":
            direction = "Base64 🡨 ASCII"
            final = UtilityCommandFunctions.convert_base64.encode(value)
        else:
            await ctx.respond("Invalid input for 'mode'.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        await ctx.respond(embed=hikari.Embed(title=f"{direction} Conversion:", description=f"```{final}```"))
    except UnicodeEncodeError:
        await ctx.respond("Found an unsupported character. I can't decode your input.", flags=hikari.MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("stats", "Get statistics on me!", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def stats_command(ctx: lightbulb.Context):
    if not await utils.validate_command(ctx):
        return

    # Unpack the tuple returned by count_lines_in_files
    lines, file_count = await utils.count_lines_in_files(directory=config.Bot.root_folder, file_extensions=[".txt", ".py", "", ".yml", ".log", ".json", ".pxd", ".pxi", ".pyi", ".hash", ".pem", ".js", ".html", ".css"])

    code_line_count = lines + 27000000 + 50000000 + 350000 + 500 + 46000#+Linux kernel +Ubuntu +CPython +Python interpreter +Discord

    command_count  = int(len(str(config.HelpMessage.message_all).split("\n"))) + int(len(str(config.HelpMessage.message_all_admin).split("\n")))

    thumbnail = os.path.join(config.Bot.assets_folder, "pfp.png")

    embed = hikari.Embed(title="Bot statistics", description="Here are some fun stats about me!")
    embed.set_thumbnail(thumbnail)
    embed.add_field("File Count:", f"I have over **{file_count}** files!", inline=False)
    embed.add_field("Code Lines:", f"I run on over **{code_line_count}** lines of code!", inline=False)
    embed.add_field("Commands Count:", f"I have **{command_count}** commands!", inline=False)

    await ctx.respond(embed=embed)

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("worm", "Watch a simulated worm", auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def worm_command(ctx: lightbulb.Context):
    if not await utils.validate_command(ctx):
        return


    if config.Bot.worm_is_running:
        await ctx.respond("There's already a simulation running. And I don't have the ressources to simulate it twice, so you'll have to wait.")
        return
    
    config.Bot.worm_is_running = True

    view = buttons.Worm()

    # Get the message object for updating
    message = await ctx.respond("Initializing worm simulator...", components=view)

    # Get text output generator from simulator
    image_generator = worm_simulator.run_worm_simulator()

    embed=hikari.Embed(title="Worm simulator", description="This is a digital simulation of the brain of the Caenorhabditis elegans worm. In 1963, Sydney Brenner proposed research into C. elegans primarily in neural development. The worm was the first organism to have it's connectome (neuronal 'wiring diagram') completed. This is a simulation of this diagram meaning every neuron and neuron connection is simulated here. (And surprisingly it is only 260 KB)\n\nThe matrix is one step closer.")
    thumbnail = hikari.File(os.path.join(config.Bot.assets_folder, "Caenorhabditis elegans.jpg"))
    embed.set_thumbnail(thumbnail)
    embed.set_author(name="Seth Miller", url="https://heyseth.github.io", icon="https://avatars.githubusercontent.com/u/8293842")
    await message.edit(embed=embed, content="", )

    # Continuously update the response message
    async for image in image_generator:
        try:
            file = hikari.File(image)
            await message.edit(attachment=file)
            await image_manager.delete(image)
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error in /worm command: {e}")
            await message.edit(f"An error occurred!{await utils.error_fun()}")
            return

@bot.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("file", "The file the question will be asked to", type=hikari.OptionType.ATTACHMENT)
@lightbulb.command("smash_or_pass", "Would you Smash or Pass?", nsfw=True, pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def smash_or_passs_command(ctx: lightbulb.Context, file:hikari.OptionType.ATTACHMENT):
    if not await utils.validate_command(ctx, nsfw=True):
        return

    supported_files = ["png", "jpg", "jpeg", "gif", "mp4", "mov"]

    file_extension = str(file).split(".")[-1].lower()

    if not file_extension in supported_files:
        await ctx.respond(f"The file {str(file)} is not a supported format. Supported formats are: {', '.join(supported_files)}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        message = await ctx.app.rest.create_message(ctx.channel_id, "Smash or Pass? 🤔", attachment=file)
    except Exception as e:
        logger.error(f"Error in /smash_or_pass during message sending: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
        return

    await message.add_reaction("❌")
    await message.add_reaction("❤️")

    await ctx.respond("Sent :)", flags=hikari.MessageFlag.EPHEMERAL)

if __name__ == "__main__":
    """
    Validates the settings
    Runs the bot
    """

    try:
        config.validate()
    except Exception as e:
        logger.error(f"An error during config validation: {e}")
        exit()

    bot.run()
