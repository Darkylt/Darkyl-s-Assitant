import lightbulb
import hikari

import bot_utils as utils


plugin = lightbulb.Plugin("Converter Binary", "Convert to or from binary")

def encode(value: str):
    """
    Encode a binary string into a text string.

    Args:
        value (str): A binary string to be encoded.
    Returns:
        str: The encoded text string.
    """
    txt=' '.join(format(ord(x), 'b') for x in value)
    return txt
    
def decode(value: str):
    """
    Decode a text string into a binary string.

    Args:
        value (str): A text string to be encoded.
    Returns:
        str: The decoded binary string.
    """
    try:
        txt=''.join([chr(int(value, 2)) for value in value.split()])
        return txt
    except ValueError:
        raise ValueError("Invalid binary string")

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("value", "The value to decode or encode", str, required=True)
@lightbulb.option("mode", "Convert Binary to ASCII or vice versa", str, required=True, choices=["text to number", "number to text"])
@lightbulb.command("converter_binary", "Convert to or from binary", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def converter_binary_command(ctx: lightbulb.SlashContext, mode:str, value:str):
    if not await utils.validate_command(ctx):
        return
    
    try:
        if mode == "text to number":
            bin = encode(value)
        elif mode == "number to text":
            bin = decode(value)
    except ValueError as ve:
        await ctx.respond("**There was an error**. I couldn't recognize your text as binary numbers.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    except Exception as e:
        from bot import logger
        logger.error(f"Error during /converter_binary command during encoding/decoding: {e}")
        await ctx.respond(f"**There was an error**. Sorry that I can't help you.\nTry this tool: https://www.duplichecker.com/text-to-binary.php", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    if len(bin) <= 480:
        await ctx.respond(f"```{bin}```", flags=hikari.MessageFlag.EPHEMERAL)
    else:
        try:
            await ctx.author.send(f"```{bin}```", flags=hikari.MessageFlag.EPHEMERAL)
            await ctx.respond("The output was too large, so I sent it to your DMs!", flags=hikari.MessageFlag.EPHEMERAL)
        except Exception as e:
            from bot import logger
            logger.error(f"An error occurred in /converter_binary during sending to author: {e}")
            await ctx.respond("There was a problem and I could not send the output", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
