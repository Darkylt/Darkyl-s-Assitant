import base64

import lightbulb
import hikari

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("Converter Base64", "Convert to or from base64")


"""
Some helper functions for encoding and decoding to and from base64 and ASCII
"""

def encode(value: str):
    """
    Encode a text string into a base64 string.

    Args:
        value (str): A text string to be encoded.
    Returns:
        str: The encoded base64 string.
    """

    sample_string_bytes = value.encode("utf-8")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string

def decode(value: str):
    """
    Decode a base64 string into a text string.

    Args:
        value (str): A base64 string to be decoded.
    Returns:
        str: The decoded text string.
    """

    base64_bytes = value.encode("utf-8")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("utf-8")
    return sample_string

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to decode or encode", str, required=True)
@lightbulb.option("mode", "Convert base64 to utf-8 or vice versa", str, required=True, choices=["text to b64", "b64 to text"])
@lightbulb.command("converter_base64", "Convert to or from base64", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_base64_command(ctx: lightbulb.SlashContext, mode:str, value:str):
    if not await utils.validate_command(ctx):
        return
    
    try:
        if mode == "text to b64":
            direction = "Base64 🡪 UTF-8"
            final = decode(value)
        elif mode == "b64 to text":
            direction = "Base64 🡨 UTF-8"
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
