import os
import random
import json
import re
from math import floor
import aiohttp
from zoneinfo import available_timezones
import datetime
import typing as t

import hikari
import lightbulb

import config_reader as config
import member_managment

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

            # Handle edgecase where ID already exists
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

async def create_user_entry(user_id: int, msg: bool, cmd: bool, rep: bool, created_at: str):
    """
    Creates an entry for the user in the database.

    Args:
        user_id (int): The User ID of the account that should be added
        msg (bool): If the event was triggered by a message
        cmd (bool): If the event was triggered by a command
        rep (bool): If the event was triggered by a report
        created_at (str): The string of when the account was created at
    """

    file = os.path.join(config.Bot.data_folder, "User Data", "user_stats.json")

    entry = {
        str(user_id):{
            "message count": 1 if msg else 0,
            "commands used": 1 if cmd else 0,
            "xp": 20,
            "level": 0,
            "reported": 1 if rep else 0,
            "created at": created_at
        }
    }

    try:
        with open(file, 'r+') as file:
            data = json.load(file)
            data.update(entry)
            file.seek(0)
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        with open(file, 'w') as file:
            json.dump(entry, file, indent=4)

async def validate_command(ctx: lightbulb.SlashContext, report: bool = False, nsfw: bool = False) -> bool:
    """
    Performs some initial processings of the command.

    Args:
        ctx: The context of the slash command
        report: Wether or not the command is a report
        nsfw: Wether or not the command is supposed to be NSFW
    Returns:
        True: Command is free to be executed
        False: One of the checks failed
    
    Processing:
        1: Checks if the command executor is a real user
        2: Adds the new info to the user statistics
    """

    try:
        if ctx.author.is_bot or ctx.author.is_system:
            await ctx.respond("This command can not be executed by other bots.", flags=hikari.MessageFlag.EPHEMERAL)
            return False
        
        if nsfw:
            channel = await ctx.app.rest.fetch_channel(ctx.channel_id)
            if not channel.is_nsfw:
                await ctx.respond("This command can only be run in a channel marked as NSFW.", flags=hikari.MessageFlag.EPHEMERAL)
                return False

        from bot import logger

        logger.info(f"{ctx.author.username} executed /{ctx.command.name}")

        try:
            await member_managment.update_user_stats(
                user_id=ctx.author.id,
                msg=False,
                cmd=True,
                rep=report,
                created_at=str(ctx.author.created_at)
            )
        except Exception as e:
            logger.error(f"An error occured while updating the user stats: {e}")
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
    try:
        choice = random.randint(0, 1) #0 means technobabble, 1 means joke

        if choice == 0:
            text = await technobabble()
        elif choice == 1:
            text = f"Let me lighten the mood with a coding joke:\n{await coding_joke()}"
        
        return f"\n{text}"
    except Exception as e:
        from bot import logger
        logger.error(f"Following error occurred during error_fun(): {e}")
        return ""

async def technobabble() -> str:
    """
    A function that does some complex stuff to generate technobabble
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
                construct = construct.replace(f, j(e),1)
            e+=1
            construct = construct[0].upper() + construct[1:]
        return str(construct)
    except Exception as e:
        from bot import logger
        logger.error(f"An error occurred while generating technobabble: {e}")
        return ""

async def coding_joke() -> str:
    try:
        params = {
            "format": "json",
            "amount": 1,
            "lang": "en"
        }

        url = "https://v2.jokeapi.dev/joke/Coding?blacklistFlags=political,racist,sexist"

        joke_txt = ""

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    type = data["type"]

                    if type == "twopart":
                            setup = data["setup"]
                            delivery = data["delivery"]
                            joke_txt = f"{setup}\n||{delivery}||"
                    elif type == "single":
                        joke = data["joke"]
                        joke_txt = joke
                    elif data["error"] == "true":
                        joke_txt = ""
                    else:
                        joke_txt = ""
                else:
                    from bot import logger
                    logger.error(f"Failed to fetch joke during error_fun: {response.status}")
                    joke_txt = ""
        
        return joke_txt
    except Exception as e:
        from bot import logger
        logger.error(f"Error during error_fun in coding_joke(): {e}")
        return ""

async def count_lines_in_files(directory, file_extensions):
    total_lines = 0
    file_count = 0

    # Step 1: List files in the directory
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
    roles = sort_roles(member.get_roles())
    if roles:
        for role in roles:
            if role.color != hikari.Color.from_rgb(0, 0, 0):
                return role.color

    return None

async def nsfw_blacklisted(user_id: int) -> bool:
    """
    A helper function that checks if a user is NSFW blacklisted/opted out of NSFW
    """

    database = os.path.join(config.Bot.data_folder, "User Data", "no_nsfw.json")

    try:
        with open(database, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data=[]
    
    if user_id in data:
        return True
    else:
        return False