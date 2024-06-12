import os
import json

import hikari.errors
import lightbulb
import hikari

import config_reader as config
import bot_utils as utils
import timed_events


plugin = lightbulb.Plugin("Tips", "Some commands for managing daily tips")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
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
        
        database = os.path.join(config.Paths.assets_folder, "Text", "tips.json")

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
        from bot import logger
        logger.error(f"An error occcurred during /admin_add_tip command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

@plugin.command
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
        
        await timed_events.random_tip(plugin.bot)

        await ctx.respond("The tip has been sent :)", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred during /admin_send_tip command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
