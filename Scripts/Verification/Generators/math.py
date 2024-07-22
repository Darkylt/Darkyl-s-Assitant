import random
from typing import Tuple

import hikari

async def generate_math_problem() -> Tuple[str, str]:
    """
    A function that generates a simple random math problem.

    Returns:
        tuple: problem(str), solution(int)
    """
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)

    if random.choice([True, False]):
        # Addition

        problem = f"{num1} + {num2}"
        solution = num1 + num2
    else:
        # Subtraction

        if num1 < num2:
            num1, num2 = num2, num1
        problem = f"{num1} - {num2}"
        solution = num1 - num2
        

    return problem, str(solution)

async def make_embed(embed: hikari.Embed, math_problem) -> hikari.Embed:

    # Edit this
    task = "Below is a simple math problem. **Please send me the solution.**"

    embed.add_field("Task:", task, inline=True)
    embed.add_field("Problem:", f"{math_problem} = ?")
    return embed

async def generate(embed: hikari.Embed, captcha_id: str) -> Tuple[hikari.Embed, str]:
    """
    This is the function that gets called when generating the captcha

    It needs to:
        Be asynchronous
        Generate an embed
        Return first embed and then the solution string
    """

    problem, solution = await generate_math_problem()

    # Perform whatever code to make the captcha
    solution = "Whatever the solution is"

    embed = await make_embed(embed, problem)
    return embed, str(solution)
