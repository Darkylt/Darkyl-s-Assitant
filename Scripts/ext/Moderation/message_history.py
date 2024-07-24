from datetime import datetime

import bot_utils as utils
import database_interaction as db
import hikari
import lightbulb

plugin = lightbulb.Plugin("Messages", "Manages message database entries")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(
    hikari.Permissions.MODERATE_MEMBERS, dm_enabled=False
)
@lightbulb.option("message_id", "The ID of the message you want", required=True)
@lightbulb.command(
    "message_history",
    "Get the previous versions of a message",
    auto_defer=True,
    ephemeral=True,
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def message_history_command(ctx: lightbulb.SlashContext, message_id: int) -> None:
    if not await utils.validate_command(ctx):
        return

    result = db.Messages.get_message_entry(message_id)

    if result is None:
        await ctx.respond(
            "Couldn't find the message you're looking for because it either doesn't exist or an error occurred."
        )
        return

    # Ensure result is a list for consistent processing
    if isinstance(result, dict):
        result = [result]  # Convert single dictionary to list

    # Limit the results to the last 10 entries because that is the embed limit
    result = result[-10:]

    # Create a list to hold embed objects
    embeds = []

    for entry in result:
        # Format date as dd.mm.yyyy HH:MM
        formatted_date = utils.iso_8601_to_discord_timestamp(entry["created_at"])

        embed = hikari.Embed(
            title=f"Version {entry['edited']}",
            description=entry["content"],
            color=0x0099FF,
        )

        author = await plugin.bot.rest.fetch_user(entry["author"])

        channel = await plugin.bot.rest.fetch_channel(entry["channel_id"])

        embed.add_field(name="Channel:", value=f"{channel.mention}", inline=False)
        embed.add_field(name="Author:", value=f"{author.mention}", inline=False)
        embed.add_field(name="Created at:", value=formatted_date, inline=False)

        embeds.append(embed)

    # Send embeds
    if embeds:
        await ctx.respond(embeds=embeds)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
