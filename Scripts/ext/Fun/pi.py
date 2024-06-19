import os
import random
import json
import hikari
import lightbulb

import bot_utils as utils
import config_reader as config

plugin = lightbulb.Plugin("pi", "Pi related commands")

pi_length = 1000000000

def formatted_number():
    return '{:,}'.format(pi_length).replace(',', '.')

@plugin.command
@lightbulb.add_cooldown(3, 3, lightbulb.GlobalBucket)
@lightbulb.option("number", "The number you want to search for", type=int, required=True)
@lightbulb.command("pi_search", "Search for a number in pi.", pass_options=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def searchpi_command(ctx: lightbulb.context.SlashContext, number) -> None:
    if not await utils.validate_command(ctx):
        return

    pi_file = os.path.join(config.Paths.assets_folder, "Text", "pi.txt")

    number_str = str(number)
    number_len = len(number_str)

    # Define chunk size (10MB)
    chunk_size = 10 * 1024 * 1024

    message = await ctx.respond("Searching...")

    try:
        with open(pi_file, "r", encoding='utf-8') as f:
            overlap = number_len - 1
            position = 0
            chunk = f.read(chunk_size)

            while chunk:
                # Search for the number in the current chunk
                index = chunk.find(number_str)

                if index != -1:
                    await message.edit(f"The number {number_str} was found at position **{position + index}** of pi.")
                    return

                # Read the next chunk, including overlap
                position += chunk_size - overlap
                f.seek(position)
                chunk = f.read(chunk_size)

                # Combine the end of the previous chunk with the new chunk to handle overlaps
                if len(chunk) > 0:
                    combined_chunk = chunk[-overlap:] + chunk[:overlap]
                    index = combined_chunk.find(number_str)
                    if index != -1:
                        # Adjust the index based on the actual position in the file
                        await message.edit(f"The number {number_str} was found at position **{position - overlap + index}** of pi.")
                        return
            
            pi_jokes_file = os.path.join(config.Paths.assets_folder, "Text", "pijokes.json")

            with open(pi_jokes_file, 'r') as jf:
                jokes = json.load(jf)
            
            joke = random.choice(jokes)

            await message.edit(f"The number {number_str} was not found in the first {formatted_number()} digits of pi.\n\nHere's a joke about pi instead:\n{joke['setup']}\n||{joke['punchline']}||")
    
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred during pi_search command: {e}")
        await message.edit(f"An error occurred! {utils.error_fun}")


@plugin.command
@lightbulb.command("pi_fact", "Get a random fact about pi.")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pi_fact_command(ctx: lightbulb.context.SlashContext) -> None:
    if not await utils.validate_command(ctx):
        return

    facts_file = os.path.join(config.Paths.assets_folder, "Text", "pifacts.txt")
    
    try:
        with open(facts_file, "r", encoding='utf-8') as file:
            facts = file.readlines()
            random_fact = random.choice(facts)
            # Splitting the first sentence
            sentences = random_fact.split(".")
            first_sentence = sentences[0] + "."
            rest_of_the_line = ".".join(sentences[1:]).strip()  # Joining the remaining sentences
            
        await ctx.respond(f"**{first_sentence}** {rest_of_the_line}")
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred during pi_fact command: {e}")
        await ctx.respond(f"An error occurred! {utils.error_fun}", flags=hikari.MessageFlag.EPHEMERAL)

def get_segment_statistic(segment: int, total_digits: int):
    str_segment = str(segment)

    frequency = {}

    for digit in str_segment:
        if digit in frequency:
            frequency[digit] += 1
        else:
            frequency[digit] = 1
    
    sorted_frequency = dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True))

    formatted_string = ""
    for digit, count in sorted_frequency.items():
        percentage = (count / total_digits) * 100
        formatted_string += f"{digit}: {count} times, {percentage:.2f}% of segment\n"
    
    return formatted_string

@plugin.command
@lightbulb.option("start", "Where should the segment start", type=int, required=True, max_value=(pi_length-1), min_value=1)
@lightbulb.option("length", "The length of the segment", type=int, required=True, max_value=1500, min_value=1)
@lightbulb.command("pi_segment", "Get a segment of pi with stats about it.", pass_options=True)
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def pi_segment_command(ctx: lightbulb.context.SlashContext, start, length) -> None:
    if not await utils.validate_command(ctx):
        return
    
    pi_file = os.path.join(config.Paths.assets_folder, "Text", "pi.txt")
    
    if start < 1 or start > (pi_length-1):
        await ctx.respond(f"Please enter a start position between 1 and {formatted_number()}.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    if length < 1 or start + length - 1 > pi_length:
        await ctx.respond(f"I can only calculate pi up to {pi_length}", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    try:

        with open(pi_file, "r") as file:
            file.seek(start - 1)
            segment = file.read(length)
            segment = segment.replace(".", "")
            segment = int(segment)

        stats = get_segment_statistic(segment, length)

        await ctx.respond(f"Your segment is:\n{segment}\n\nHere are some statistics about your segment:\n{stats}")
    
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred in /pi_segment command: {e}")
        await ctx.respond(f"An error occurred! {utils.error_fun}", flags=hikari.MessageFlag.EPHEMERAL)

async def count_characters_in_file(file_path, chunk_size=1024*1024):
    """
    Counts the number of characters in a file without loading the entire file into memory.
    
    Args:
        file_path (str): The path to the file.
        chunk_size (int): The size of the chunks to read the file in bytes. Default is 1MB.

    Returns:
        int: The total number of characters in the file.
    """
    total_characters = 0

    with open(file_path, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            total_characters += len(chunk)
    
    return total_characters

async def count_pi():
    global pi_length

    from bot import logger

    logger.info("Counting pi.txt")

    pi_file = os.path.join(config.Paths.assets_folder, "Text", "pi.txt")
    pi_length = await count_characters_in_file(pi_file)

    logger.info("Finished counting pi.txt")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove(plugin)
