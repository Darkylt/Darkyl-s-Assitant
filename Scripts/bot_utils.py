import os
import random
import re
from math import floor
import aiohttp
import datetime
import typing as t
import logging

import hikari
import hikari.errors
import lightbulb

import member_managment
import database_interaction

async def generate_id(folder=None):
    """
    Generates a uuid
    
    Args:
        folder: If provided, checks if the id is already contained in a folder
    Returns:
        id (str): The generated uuid
        None: If an error occurred
    """
    from uuid import uuid4

    while True:
        try:
            id = str(uuid4())

            # Checks if the ID is already contained in a folders filenames
            if folder:
                if not any(id in filename for filename in os.listdir(folder)):
                    return id
            else:
                return id
        except Exception as e:
            from bot import logger
            logger.error(f"Error during ID Generation: {e}")
            return None

async def choose_random_file(folder_path: str):
    """
    Takes in a path and returns the path to a random file in that directory
    """
    # Check if the provided path is a directory
    if not os.path.isdir(folder_path):
        return "Error: The provided path is not a directory."

    # Get a list of all files in the directory
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Check if the directory is empty
    if not files:
        return "Error: The directory is empty."

    # Choose a random file from the list
    random_file = random.choice(files)

    # Return the path to the randomly chosen file
    return str(os.path.join(folder_path, random_file))

async def validate_command(ctx: lightbulb.Context, report: bool = False, nsfw: bool = False, message_command: bool = False) -> bool:
    """
    Performs some initial processing of a command.

    Args:
        ctx: The context of the command
        report: Whether or not the command is a report
        nsfw: Whether or not the command is supposed to be NSFW
        message_command: Whether or not the command is a message command
    Returns:
        True: Command is free to be executed
        False: One of the checks failed
    
    Processing:
        1: Checks if the command executor is a real user
        2: If nsfw, performs checks to validate the usage of the command
        3: Adds the new info to the user statistics
    """

    from bot import logger

    try:
        # Is command author human?
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This command cannot be executed by other bots.", flags=hikari.MessageFlag.EPHEMERAL)
            return False
        
        if nsfw:
            try:
                # Check if it's an nsfw channel
                channel = await ctx.app.rest.fetch_channel(ctx.channel_id)
                if not channel.is_nsfw:
                    await ctx.respond("This command can only be run in a channel marked as NSFW.", flags=hikari.MessageFlag.EPHEMERAL)
                    return False

                # Check if the command author is nsfw blacklisted
                if await nsfw_blacklisted(ctx.author.id):
                    await ctx.respond("You opted out of NSFW commands.", flags=hikari.MessageFlag.EPHEMERAL)
                    return False
            except hikari.errors.ForbiddenError:
                await ctx.respond("I do not have access to this channel.", flags=hikari.MessageFlag.EPHEMERAL)
                return False
            except hikari.errors.NotFoundError:
                await ctx.respond("The channel was not found.", flags=hikari.MessageFlag.EPHEMERAL)
                return False
            except Exception as e:
                
                logger.error(f"An error occurred during NSFW checks: {e}")
                await ctx.respond("An error occurred while performing checks.", flags=hikari.MessageFlag.EPHEMERAL)
                return False

        if message_command:
            logger.info(f"{ctx.author.username}({ctx.author.id}) used {ctx.command.name} command")
        else:
            logger.info(f"{ctx.author.username}({ctx.author.id}) executed /{ctx.command.name}")

        # Update stats
        try:
            id = ctx.author.id.real

            await member_managment.update_user_stats(
                user_id=int(id),
                msg=False,
                cmd=True,
                rep=report
            )
        except Exception as e:
            logger.error(f"An error occurred while updating the user stats: {e}")
            await ctx.respond("An error occurred while updating the user stats.", flags=hikari.MessageFlag.EPHEMERAL)
            return False

        return True
    except Exception as e:
        logger.error(f"Error while validating during /{ctx.command.name}: {e}")
        await ctx.respond("An error occurred.", flags=hikari.MessageFlag.EPHEMERAL)
        return False
    
async def uwu_maker(text: str):
    """
    A function for 'owoifying' text

    Args:
        text (str): The text that should be processed
    Returns:
        text (str): The processed text

    Example:
        Pre: Lorem ipsum dolor sit amet
        Post: Wowem ipsum dowow sit amet
    """

    faces = ["owo", "UwU", ">w<", "^w^"]
    v = text
    r = re.sub('[rl]', "w", v)
    r = re.sub('[RL]', "W", r)
    r = re.sub('ove', 'uv', r)
    r = re.sub('n', 'ny', r)
    r = re.sub('N', 'NY', r)
    r = re.sub('[!]', " " + random.choice(faces) + " ", r + "~")
    return r

jargonWordPool = [["TCP", "HTTP", "SDD", "RAM", "GB", "CSS", "SSL", "AGP", "SQL", "FTP", "PCI", "AI", "ADP", "RSS", "XML", "EXE", "COM", "HDD", "THX", "SMTP", "SMS", "USB", "PNG", "PHP", "UDP", "TPS", "RX", "ASCII", "CD-ROM", "CGI", "CPU", "DDR", "DHCP", "BIOS", "IDE", "IP", "MAC", "MP3", "AAC", "PPPoE", "SSD", "SDRAM", "VGA", "XHTML", "Y2K", "GUI"],
                ["auxiliary", "primary", "back-end", "digital", "open-source", "virtual", "cross-platform", "redundant", "online", "haptic", "multi-byte", "bluetooth", "wireless", "1080p", "neural", "optical", "solid state", "mobile", "unicode", "backup", "high speed", "56k", "analog", "fiber optic", "central", "visual", "ethernet", "encrypted", "decrypted"],
                ["driver", "protocol", "bandwidth", "panel", "microchip", "program", "port", "card", "array", "interface", "system", "sensor", "firewall", "hard drive", "pixel", "alarm", "feed", "monitor", "application", "transmitter", "bus", "circuit", "capacitor", "matrix", "address", "form factor", "array", "mainframe", "processor", "antenna", "transistor", "virus", "malware", "spyware", "network", "internet"],
                ["back up", "bypass", "hack", "override", "compress", "copy", "navigate", "index", "connect", "generate", "quantify", "calculate", "synthesize", "input", "transmit", "program", "reboot", "parse", "shut down", "inject", "transcode", "encode", "attach", "disconnect", "network"],
                ["backing up", "bypassing", "hacking", "overriding", "compressing", "copying", "navigating", "indexing", "connecting", "generating", "quantifying", "calculating", "synthesizing", "inputting", "transmitting", "programming", "rebooting", "parsing", "shutting down", "injecting", "transcoding", "encoding", "attaching", "disconnecting", "networking"]
            ]

jargonConstructs = ["If we {3} the {2}, we can get to the {0} {2} through the {1} {0} {2}!", "We need to {3} the {1} {0} {2}!", "Try to {3} the {0} {2}, maybe it will {3} the {1} {2}!", "You can't {3} the {2} without {4} the {1} {0} {2}!", "Use the {1} {0} {2}, then you can {3} the {1} {2}!", "The {0} {2} is down, {3} the {1} {2} so we can {3} the {0} {2}!", "{4} the {2} won't do anything, we need to {3} the {1} {0} {2}!", "I'll {3} the {1} {0} {2}, that should {3} the {0} {2}!", "My {0} {2} is down, our only choice is to {3} and {3} the {1} {2}!", "They're inside the {2}, use the {1} {0} {2} to {3} their {2}!", "Send the {1} {2} into the {2}, it will {3} the {2} by {4} its {0} {2}!"]

async def error_fun() -> str:
    """
    A function for spicing up error messages.
    Chooses either to generate random technobabble or a coding joke

    Returns:
        A string with either a joke or technobabble
        An empty string if an error occurred
    """
    try:
        choice = random.randint(0, 1)  # 0 means technobabble, 1 means joke

        if choice == 0:
            text = await technobabble()
        else:
            joke = await coding_joke()
            text = f"Let me lighten the mood with a coding joke:\n{joke}"
        
        if not text:
            return ""
        return f"\n{text}"
    except Exception as e:
        from bot import logger
        logger.error(f"Following error occurred during error_fun(): {e}")
        return ""

async def technobabble() -> str:
    """
    A function that does some complex stuff to generate technobabble

    Returns:
        A randomly generated sentence
        An empty string if an error occurred
    """
    try:
        h = []

        def j(b):
            c = jargonWordPool[b]
            e = floor(random.random() * len(c))
            f = c[e]
            while f in h:
                f = c[floor(random.random() * len(c))]
            h.append(f)
            return f
        
        rnd = floor(random.random() * len(jargonConstructs))
        construct = jargonConstructs[rnd]

        e = 0
        while e < len(jargonWordPool):
            f = "{" + str(e) + "}"
            while construct.find(f) > -1:
                construct = construct.replace(f, j(e), 1)
            e += 1

        construct = construct[0].upper() + construct[1:]
        return str(construct)
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred while generating technobabble: {e}")
        return ""

async def coding_joke() -> str:
    """
    A function to get a coding joke from jokeapi.dev

    Returns:
        The joke
        An empty string if an error occurred 
    """
    url = "https://v2.jokeapi.dev/joke/Coding?blacklistFlags=political,racist,sexist"
    params = {
        "format": "json",
        "amount": 1,
        "lang": "en"
    }

    try:
        from bot import logger
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("error"):
                        return ""
                    if data["type"] == "twopart":
                        return f"{data['setup']}\n||{data['delivery']}||"
                    elif data["type"] == "single":
                        return data["joke"]
                else:
                    logger.error(f"Failed to fetch joke during error_fun: {response.status}")
        return ""
    except aiohttp.ServerTimeoutError:
        logger.error(f"Failed to fetch coding joke: API timed out.")
        return ""
    except Exception as e:
        logger.error(f"Error during error_fun in coding_joke(): {e}")
        return ""

async def count_lines_in_files(directory, file_extensions: list[str] = [".txt", ".py", "", ".yml", ".log", ".json", ".pxd", ".pxi", ".pyi", ".hash", ".pem", ".js", ".html", ".css"]):
    """
    A function that counts the lines in the files for a given directory

    Args:
        directory: The path to the directory that should be counted
        file_extensions (list): A list of file extensions that should by counted
    
    Returns:
        total_lines: The total number of counted lines
        file_count: The total number of counted files
    """
    total_lines = 0
    file_count = 0

    # List files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if the file has no extension
            if not file_extensions and '.' not in file:
                try:
                    # Count lines in each file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        file_count += 1
                except UnicodeDecodeError:
                    pass
                except Exception as e:
                    pass

            # Check if the file has an extension matching the provided list
            elif any(file.endswith(ext) for ext in file_extensions):
                try:
                    # Count lines in each file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                        file_count += 1
                except UnicodeDecodeError:
                    pass
                except Exception as e:
                    pass

    return (total_lines), file_count

def format_dt(time: datetime.datetime, style: str | None = None) -> str:
    """Convert a datetime into a Discord timestamp.

    For styling see this link: https://discord.com/developers/docs/reference#message-formatting-timestamp-styles.
    """
    valid_styles = ["t", "T", "d", "D", "f", "F", "R"]

    if style and style not in valid_styles:
        raise ValueError(f"Invalid style passed. Valid styles: {' '.join(valid_styles)}")

    if style:
        return f"<t:{int(time.timestamp())}:{style}>"

    return f"<t:{int(time.timestamp())}>"

BADGE_MAPPING = {
    hikari.UserFlag.BUG_HUNTER_LEVEL_1: "`Bug Hunter`",
    hikari.UserFlag.BUG_HUNTER_LEVEL_2: "`Bug Hunter Gold`",
    hikari.UserFlag.DISCORD_CERTIFIED_MODERATOR: "`Official Discord Moderator`",
    hikari.UserFlag.EARLY_SUPPORTER: "`Early Supporter`",
    hikari.UserFlag.EARLY_VERIFIED_DEVELOPER: "`Early verified developer`",
    hikari.UserFlag.HYPESQUAD_EVENTS: "`Hypesquad Events`",
    hikari.UserFlag.HYPESQUAD_BALANCE: "`Hypesquad Balance`",
    hikari.UserFlag.HYPESQUAD_BRAVERY: "`Hypesquad Bravery`",
    hikari.UserFlag.HYPESQUAD_BRILLIANCE: "`Hypesquad Brilliance`",
    hikari.UserFlag.PARTNERED_SERVER_OWNER: "`Discord Partner`",
    hikari.UserFlag.DISCORD_EMPLOYEE: "`Discord Employee`",
    hikari.UserFlag.ACTIVE_DEVELOPER: "`Active Developer`",
    hikari.UserFlag.VERIFIED_BOT: "`Verified Bot`"
}

def get_badges(user: hikari.User) -> t.Sequence[str]:
    """Return a list of badge emojies that the user has."""
    return [emoji for flag, emoji in BADGE_MAPPING.items() if flag & user.flags]

def sort_roles(roles: t.Sequence[hikari.Role]) -> t.Sequence[hikari.Role]:
    """Sort a list of roles in a descending order based on position."""
    return sorted(roles, key=lambda r: r.position, reverse=True)

def get_color(member: hikari.Member) -> hikari.Color | None:
    """A function that gets the color of a profile from a hikari.Member object"""
    roles = sort_roles(member.get_roles())
    if roles:
        for role in roles:
            if role.color != hikari.Color.from_rgb(0, 0, 0):
                return role.color

    return None

async def nsfw_blacklisted(user_id: int) -> bool:
    """
    A helper function that checks if a user is NSFW blacklisted/opted out of NSFW

    Args:
        user_id (int): The id of the user you want to enter
    Returns:
        True: User is blacklisted
        False: User isn't blacklisted
    """

    entry = database_interaction.get_user_entry(user_id, values=["nsfw_opt_out"])

    nsfw_opt_out = bool(entry[0])

    return nsfw_opt_out
