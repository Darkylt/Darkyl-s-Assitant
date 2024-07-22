"""
A template so I can remember how to write new captchas
"""

from typing import Tuple

import hikari

async def make_embed(embed: hikari.Embed) -> hikari.Embed:

    # Edit this
    task = "DESCRIBE WHAT THE USER HAS TO DO"

    embed.add_field("Task:", task, inline=True)
    return embed

async def generate(embed: hikari.Embed, captcha_id: str) -> Tuple[hikari.Embed, str]:
    """
    This is the function that gets called when generating the captcha

    It needs to:
        Be asynchronous
        Generate an embed
        Return first embed and then the solution string
    """

    # Perform whatever code to make the captcha
    solution = "Whatever the solution is"

    embed = await make_embed(embed)
    return embed, str(solution)
