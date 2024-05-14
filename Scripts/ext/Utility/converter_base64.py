import base64

import lightbulb
import hikari

import bot_utils as utils

plugin = lightbulb.Plugin("Converter Base64", "Convert to or from base64")

"""
Some helper functions for encoding and decoding to and from base64 and ASCII
"""

def encode(value: str):
    """
    Encode a base64 string into a text string.

    Args:
        value (str): A base64 string to be encoded.
    Returns:
        str: The encoded text string.
    """

    sample_string = value
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64decode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def decode(value: str):
    """
    Decode a text string into a base64 string.

    Args:
        value (str): A text string to be encoded.
    Returns:
        str: The decoded base64 string.
    """

    base64_string = value
    base64_bytes = base64_string.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string


@plugin.command
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
            final = decode(value)
        elif mode == "encode":
            direction = "Base64 🡨 ASCII"
            final = encode(value)
        else:
            await ctx.respond("Invalid input for 'mode'.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        await ctx.respond(embed=hikari.Embed(title=f"{direction} Conversion:", description=f"```{final}```"))
    except UnicodeEncodeError:
        await ctx.respond("Found an unsupported character. I can't decode your input.", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
