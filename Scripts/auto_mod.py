import os
import json
import asyncio

import hikari

import config_reader as config
import buttons
import bot_utils as utils

async def check_attachments(attachments) -> str:
    """
    Returns true if the attachments aren't valid
    """
    allowed_files = config.AutoMod.allowed_files
    allowed_extensions = tuple('.' + ext for ext in allowed_files)

    for attachment in attachments:
        filename = str(attachment.filename)
        filetype = filename.split(".")[-1]
        if not filetype in config.AutoMod.allowed_files:
            return filename
        
    return False

async def check_message(content: str, nsfw: bool) -> list:
    """
    A function that performs various checks on a message to moderate it.

    Args:
        content (str): The content of the message
        nsfw (bool): Was the message sent in a channel marked as nsfw?
    Returns:
        bool: True if the message violates any moderation rules, False otherwise.
    """
    violations = []
    try:
        if not nsfw:
            if await check_for_porn(content=content):
                violations.append("Pornographic content")
            if config.AutoMod.filter_nsfw_language:
                if await check_for_nswf(content=content):
                    violations.append("NSFW language")
        
        if await check_for_fakenews(content=content):
            violations.append("Fake news links")
        
        if await check_for_gambling(content=content):
            violations.append("Gambling links")
    except Exception as e:
        from bot import logger
        logger.error(f"Error during check_message(): {e}")

    return violations

async def check_for_fakenews(content: str) -> bool:
    """
    A function that checks if the message contains a banned fake news link.

    Args:
        content (str): The content of the message
    Returns:
        bool: True if the message contains a banned fake news link, False otherwise.
    """
    try:
        banned_links_path = os.path.join(config.Bot.data_folder, "Banned Content", "Websites", "fakenews.txt")
        with open(banned_links_path, 'r') as file:
            banned_links = file.read().splitlines()
        
        for link in banned_links:
            if link in content:
                return True
    except Exception as e:
        from bot import logger
        logger.error(f"Error during check_for_fakenews(): {e}")

async def check_for_gambling(content: str) -> bool:
    """
    A function that checks if the message contains a banned gambling link.

    Args:
        content (str): The content of the message
    Returns:
        bool: True if the message contains a banned gambling link, False otherwise.
    """
    try:
        banned_links_path = os.path.join(config.Bot.data_folder, "Banned Content", "Websites", "gambling.txt")
        with open(banned_links_path, 'r') as file:
            banned_links = file.read().splitlines()
        
        for link in banned_links:
            if link in content:
                return True
    except Exception as e:
        from bot import logger
        logger.error(f"Error during check_for_gambling(): {e}")

async def check_for_porn(content: str) -> bool:
    """
    A function that checks if the message contains a banned porn link.

    Args:
        content (str): The content of the message
    Returns:
        bool: True if the message contains a banned porn link, False otherwise.
    """
    try:
        # Check for banned porn links
        banned_links_path = os.path.join(config.Bot.data_folder, "Banned Content", "Websites", "porn.txt")
        with open(banned_links_path, 'r') as file:
            banned_links = file.read().splitlines()

        for link in banned_links:
            if link in content:
                return True
    except Exception as e:
        from bot import logger
        logger.error(f"Error during check_for_porn(): {e}")

async def check_for_nswf(content: str) -> bool:
    """
    A function that checks if the message contains a banned word.

    Args:
        content (str): The content of the message
    Returns:
        bool: True if the message contains a banned word, False otherwise.
    """

    # Check for NSFW words
    try:
        banned_words_folder = os.path.join(config.Bot.data_folder, "Banned Content", "Words", "NSFW Words")
        nsfw_words_files = os.listdir(banned_words_folder)

        for filename in nsfw_words_files:
            with open(os.path.join(banned_words_folder, filename), 'r', encoding='utf-8') as file:
                nsfw_words = file.read().splitlines()
                for word in nsfw_words:
                    if word.lower() in content.lower():
                        return True
    except Exception as e:
        from bot import logger
        logger.error(f"Error during check_for_nsfw(): {e}")

    return False


""" REPORT SECION """
# Section that handles the reporting

def create_report_embed(event: hikari.MessageCreateEvent, violations: list) -> hikari.Embed:
    """Creates an embed for the violation report."""
    try:
        report_embed = hikari.Embed(
            title="**Report**",
            description=f"**AutoMod** has reported {event.author.mention}.",
            color=hikari.Color.from_hex_code("#fc0000")
        )
        report_embed.set_thumbnail(event.author.make_avatar_url())
        report_embed.add_field("**Reported User:**", value=f"{event.author.mention} `({event.author_id})`")
        report_embed.add_field("**Reason:**", value=f"Message contains the following violations:\n{', '.join(violations)}")
        report_embed.add_field("**Original Message:**", value=event.message.content)
        return report_embed
    except Exception as e:
        from bot import logger
        logger.error(f"Error during create_report_embed(): {e}")

def update_report_data(user_id, message_id: int, violations: list):
    """Updates the report data."""
    try:
        database_path = os.path.join(config.Bot.data_folder, "User Data", "reports.json")
        report_data = {}

        if os.path.exists(database_path) and os.path.getsize(database_path) > 0:
            with open(database_path, "r") as file:
                try:
                    report_data = json.load(file)
                except json.JSONDecodeError:
                    pass

        user_id = str(user_id)
        if user_id not in report_data:
            report_data[user_id] = {"reasons": {}}

        reason = f"Message contains the following violations:\n{', '.join(violations)} {asyncio.run(utils.generate_id())}"
        report_data[user_id]["reasons"][reason] = {"reporter": "AutoMod", "report_message": message_id}

        with open(database_path, "w") as file:
            json.dump(report_data, file, indent=4)
    except Exception as e:
        from bot import logger
        logger.error(f"Error during update_report_data(): {e}")

async def handle_violations(event: hikari.MessageCreateEvent, violations: list):
    """Handles violations detected by auto moderation."""
    try:
        violation_message = (
            f"Your message contains the following violations:\n{', '.join(violations)}\n\n"
            "You will be reported to a mod.\nIf you believe this is an error or unnecessary, "
            "please message a mod or an admin."
        )
        await event.message.respond(violation_message, flags=hikari.MessageFlag.EPHEMERAL)

        report_embed = create_report_embed(event, violations)
        return report_embed
    except Exception as e:
        from bot import logger
        logger.error(f"Error during handle_violations(): {e}")