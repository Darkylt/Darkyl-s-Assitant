import os
import json

import hikari.errors
import lightbulb
import hikari

import bot_utils as utils
import buttons
import config_reader as config
import image_manager
import database_interaction

plugin = lightbulb.Plugin("ModMenu", "A control panel for a user")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.BAN_MEMBERS))

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.BAN_MEMBERS, dm_enabled=False)
@lightbulb.option("user", "The target", type=hikari.User)
@lightbulb.command("mod_menu", "Your control panel for a user", pass_options=True, auto_defer=True, ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def mod_menu_command(ctx: lightbulb.SlashContext, user: hikari.User):
    if not await utils.validate_command(ctx):
        return
    
    # Fetch user to get extra info available
    user = await ctx.app.rest.fetch_member(ctx.guild_id, user.id)

    banner = await image_manager.download_image(user.banner_url, user.id)

    if banner == None:
        color = utils.get_color(user)
    else:
        if banner.endswith("gif"):
            banner = await image_manager.gif_to_png(banner)

        avg_red, avg_green, avg_blue = image_manager.average_color(str(banner))
        color = hikari.Color.from_rgb(int(avg_red), int(avg_green), int(avg_blue))

    embed = hikari.Embed(
        title=f"**Mod Menu:** {user.username}",
        description=f"This is a mod menu for this user. Here you can access most important information and quickly perform actions!",
        color=color
        )
    user_avatar = user.avatar_url
    if user_avatar != None:
        embed.set_thumbnail(user_avatar)
    
    embed.add_field("**• Nickname:**", value=f"{user.display_name or '-'}")
    embed.add_field("**• User ID:**", value=f"{user.id}")
    embed.add_field("**• Bot:**", value=f"'{user.is_bot}'")
    embed.add_field("**• Account create date:**", value=f"{utils.format_dt(user.created_at)} ({utils.format_dt(user.created_at, style='R')})")
    embed.add_field("**• Joined at:**", value=f"{utils.format_dt(user.joined_at)} ({utils.format_dt(user.joined_at, style='R')})")
    embed.add_field("**• Badges:**", value="   ".join(utils.get_badges(user)) or "`-`")
    embed.add_field("**• Timed out:**", value=f"Until: {utils.format_dt(user.communication_disabled_until()) if user.communication_disabled_until() is not None else '-'}")

    stats = database_interaction.get_user_entry(user_id=user.id)

    if stats:
        (id, msg_count, xp, level, cmds_used, reported, been_reported, nsfw_opt_out) = stats

        embed.add_field("**• Messages Sent:**", value=msg_count)
        embed.add_field("**• Commands Used:**", value=cmds_used)
        embed.add_field("**• XP:**", value=xp)
        embed.add_field("**• Level:**", value=level)
        embed.add_field("**• Opted Out of NSFW:**", value=bool(nsfw_opt_out))

    roles_list = [role.mention for role in utils.sort_roles(user.get_roles()) if role.id != ctx.guild_id]
    roles = ", ".join(roles_list) if roles_list else "`-`"
    embed.add_field("**• Roles:**", value=f"{roles}")

    warnings_file = os.path.join(config.Paths.data_folder, "User Data", "warnings.json")

    if os.path.exists(warnings_file):
        with open(warnings_file, "r") as file:
            warnings_data = json.load(file)
            user_warnings = warnings_data.get(str(user.id), [])
            if user_warnings:
                warnings_text = "\n\n".join([f"`{warning}`" for warning in user_warnings])
                embed.add_field("**• Warnings:**", value=warnings_text)
            else:
                embed.add_field("**• Warnings:**", value="No warnings")
    else:
        embed.add_field("**• Warnings:**", value="Couldn't find the warnings database.")

    if stats:
        embed.add_field("**• Reported user:**", value=reported)
        embed.add_field("**• Been reported:**", value=been_reported)

    reports_file = os.path.join(config.Paths.data_folder, "User Data", "reports.json")

    if os.path.exists(reports_file):
        with open(reports_file, "r") as file:
            reports_data = json.load(file)
            user_reports = reports_data.get(str(user.id), {})
            if user_reports:
                reasons = user_reports.get("reasons", {})
                if reasons:
                    reasons_text = ""
                    for reason, details in reasons.items():
                        reporter = details.get("reporter")
                        if reporter.isdigit():
                            reporter_user = await ctx.app.rest.fetch_user(reporter)
                            reporter_mention = f"{reporter_user.mention}"
                        else:
                            reporter_mention = reporter
                        reasons_text += f"`{reason}`\nBy {reporter_mention}\n\n"
                    embed.add_field("**• Reports:**", value=reasons_text.strip() or "No reports for this user")
                else:
                    embed.add_field("**• Reports:**", value="No reports for this user")
            else:
                embed.add_field("**• Reports:**", value="No reports for this user")
    else:
        embed.add_field("**• Reports:**", value="Couldn't find the reports database.")

    if banner != None:
        embed.set_image(user.banner_url)

    view = buttons.ModMenu()

    await ctx.respond(f"{user.mention}", embed=embed, components=view)

    if banner != None:
        os.remove(banner)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
