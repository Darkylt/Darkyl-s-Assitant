import asyncio
import datetime

import bot_utils as utils
import buttons
import config_reader as config
import hikari
import lightbulb
import miru
import miru.client

plugin = lightbulb.Plugin("Test", "Some test stuff for admins")
plugin.add_checks(lightbulb.has_role_permissions(hikari.Permissions.ADMINISTRATOR))


ENABLED = True


async def test(ctx: lightbulb.SlashContext):
    embed = hikari.Embed(
        title="Pings",
        description="What would you like to be pinged for?\n🔴: **YouTube Uploads**\n\n🟣: **Twitch Streams**\n\n📣: **Announcements**\n\n",
        color=hikari.Color.from_hex_code("#77f599"),
    )

    view = buttons.ReactionRoles.Pings()

    await ctx.app.rest.create_message(1234404378715230289, embed=embed, components=view)


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.app_command_permissions(hikari.Permissions.ADMINISTRATOR, dm_enabled=False)
@lightbulb.command("admin_test", "A command used for testing the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def test_command(ctx: lightbulb.SlashContext):
    """
    A command used to test the bot.
    It performs some basic checks and then executes the test() function
    """
    if not await utils.validate_command(ctx):
        return

    try:
        if not ctx.author.id == config.Bot.darkyl_id:
            await ctx.respond(
                "This command can only be used by Darkyl.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        if not ENABLED:
            await ctx.respond("Command disabled.", flags=hikari.MessageFlag.EPHEMERAL)
            return
    except Exception as e:
        print(f"An error occurred while processing the /admin_tst command {e}")

    try:
        await test(ctx)
    except Exception as e:
        print(f"An error occurred during the test: {e}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove(plugin)
