import bot_utils as utils
import config_reader as config
import hikari
import hikari.errors
import lightbulb

plugin = lightbulb.Plugin("role_managment", "Allows mods to manage roles with commands")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.MANAGE_ROLES))


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The user you want to give a role", hikari.Member, required=True
)
@lightbulb.option(
    "role", "The role you want to give to the user", hikari.Role, required=True
)
@lightbulb.app_command_permissions(hikari.Permissions.MANAGE_ROLES, dm_enabled=False)
@lightbulb.command(
    "add_role",
    "Give a role to a user.",
    auto_defer=True,
    pass_options=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def add_role_command(
    ctx: lightbulb.SlashContext, user: hikari.Member, role: hikari.Role
) -> None:
    if not await utils.validate_command(ctx):
        return
    try:
        await user.add_role(
            role, reason=f"Rolle added via command by {ctx.author.username}"
        )
        await ctx.respond(f"Added {role.mention} to {user.mention}.")
    except hikari.errors.ForbiddenError:
        await ctx.respond(
            "I do not have permission to add the role.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


@plugin.command()
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option(
    "user", "The user you want to remove the role from.", hikari.Member, required=True
)
@lightbulb.option(
    "role", "The role you want to remove from the user", hikari.Role, required=True
)
@lightbulb.app_command_permissions(hikari.Permissions.MANAGE_ROLES, dm_enabled=False)
@lightbulb.command(
    "remove_role",
    "Remove a role of a user.",
    auto_defer=True,
    pass_options=True,
    ephemeral=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def add_role_command(
    ctx: lightbulb.SlashContext, user: hikari.Member, role: hikari.Role
) -> None:
    if not await utils.validate_command(ctx):
        return
    try:
        await user.remove_role(
            role, reason=f"Rolle removed via command by {ctx.author.username}"
        )
        await ctx.respond(f"Removed {role.mention} from {user.mention}.")
    except hikari.errors.ForbiddenError:
        await ctx.respond(
            "I do not have permission to remove the role.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
