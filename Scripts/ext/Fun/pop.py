import random

import lightbulb
import hikari

import bot_utils as utils

plugin = lightbulb.Plugin("pop", "Get something to do")


@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.UserBucket)
@lightbulb.command("pop", "Occupational therapy")
@lightbulb.implements(lightbulb.SlashCommand)
async def pop_command(ctx: lightbulb.SlashContext):
    if not await utils.validate_command(ctx):
        return
    try:
        bubble = "||*pop*||"
        non_bubble = "〰"
        emojis = ["🌊", "〰️", "♒︎", "〽", "🌀", "༄", "˚", "﹏", "࿐", "≈", "🦈", "𓍢ִ", "𓊝", "˖", "💦", "⛆", "🐬", "ৎ", "౨", "໑"]

        num_repeats = random.randint(100, 400)
        string_list = [non_bubble] * num_repeats

        num_bubbles = random.randint(1, num_repeats // 2)
        bubble_positions = random.sample(range(num_repeats), num_bubbles)

        for pos in bubble_positions:
            string_list[pos] = bubble
        
        for i, char in enumerate(string_list):
            if char == non_bubble and random.random() < 0.3:
                random_emoji = random.choice(emojis)
                string_list[i] = random_emoji
        
        result_string = "".join(string_list)

        await ctx.respond(f"Here you go:\n\n{result_string}", flags=hikari.MessageFlag.EPHEMERAL)
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred during /pop: {e}")
        await ctx.respond(f"An error occurred!{await utils.error_fun()}", flags=hikari.MessageFlag.EPHEMERAL)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
