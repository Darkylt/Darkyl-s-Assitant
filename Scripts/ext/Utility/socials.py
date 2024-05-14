import os

import hikari.errors
import lightbulb
import hikari

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("Socials", "A socials command")

@plugin.command
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
        from bot import logger
        logger.error(f"An error occurred during the /socials command: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
