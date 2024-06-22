import random
import aiohttp
import re

import lightbulb
import hikari

import bot_utils as utils
import config_reader as config


plugin = lightbulb.Plugin("Joke", "Let me tell you a joke! (Some might be offensive, be careful.)")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.option("language", "The language of the joke", str, required=False, default = "en", choices = ["cs","de","en","es","fr","pt"])
@lightbulb.command("joke", "Let me tell you a joke! (Some might be offensive, be careful.)")
@lightbulb.implements(lightbulb.SlashCommand)
async def joke_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    
    lang = ctx.options.language

    params = {
        "format": "json",
        "amount": 1,
        "lang": lang
    }

    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=political,racist,sexist"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    joke_category = data["category"]
                    type = data["type"]

                    if type == "twopart":
                        setup = data["setup"]
                        delivery = data["delivery"]
                        joke_txt = f"{setup}\n||{delivery}||"
                    elif type == "single":
                        joke = data["joke"]
                        joke_txt = joke
                    elif data["error"] == "true":
                        await ctx.respond(f"An error occurred in the joke API!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
                        return
                    else:
                        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
                        return
                    
                    txt = random.choice([
                        "Here's the joke",
                        "Here's my joke for you",
                        "Here's my joke",
                        "Ready to crack up? Here it goes",
                        "Time to sprinkle some laughter! Here's one for you",
                        "Get ready for a dose of humor",
                        "Knock, knock! Who's there? A joke just for you",
                        "Hold onto your sides, here comes a good one",
                        "Brace yourself for a burst of laughter",
                        "Are you ready to LOL? Here we go"
                        "Get your chuckle muscles ready",
                        "Warning: hilarity incoming",
                        "Incoming joke missile, prepare to laugh",
                        "Ready for a dose of humor? Here it is",
                        "Get set to ROFL",
                        "Here's a little joke to lighten things up"
                    ])

                    await ctx.respond(f"{txt}:\n\n{joke_txt}")

                else:
                    from bot import logger
                    logger.error(f"Failed to fetch joke: {response.status}")
                    await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger
        logger.error(f"Error in /{ctx.command.name}: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
