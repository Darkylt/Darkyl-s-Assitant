import os

import lightbulb
import hikari

import bot_utils as utils
import config_reader as config


plugin = lightbulb.Plugin("Help", "Get help with the bot.")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("category", "Which category of commands are you interested in?", required=False, choices=["All", "Fun", "Utility"])
@lightbulb.command("help", "Get help with the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def help_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    
    try:
        category = ctx.options.category

        thumbnail = os.path.join(config.Paths.assets_folder, "pfp.png")

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
        from bot import logger
        logger.error(f"Error during /help command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
