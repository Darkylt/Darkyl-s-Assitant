import asyncio
import datetime

import lightbulb
import hikari
import miru
import miru.client

import bot_utils as utils
import config_reader as config
import buttons

plugin = lightbulb.Plugin("Custom Role", "Give a custom role to someone.")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.option("role_name", "The name of the role", str, required=True, max_length=100, min_length=1)
@lightbulb.option("user", "The user to assignt the role to", hikari.Member, required=True)
@lightbulb.option("color", "Color in hex", str, required=False, default="95adad")
@lightbulb.command("custom_role", "Give a custom role to someone.", pass_options=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def custom_role_command(ctx: lightbulb.SlashContext, role_name: str, user: hikari.Member, color: str):
    if not await utils.validate_command(ctx):
        return
    
    role = await plugin.app.rest.create_role(ctx.guild_id, name=role_name, color=hikari.Color.from_hex_code(color))

    await plugin.app.rest.add_role_to_member(ctx.guild_id, user, role, reason=f"Custom role assigned by {ctx.author.username}.")

    await ctx.respond(f"New role {role.mention} added to {user.mention}!", flags=hikari.MessageFlag.EPHEMERAL)
    

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
