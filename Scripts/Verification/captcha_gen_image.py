import os
import random
import string

from captcha.image import ImageCaptcha
from PIL import Image

import config_reader as config
import bot_utils as utils

async def get_all_file_paths(folder: str) -> list:
    """
    Gets all files paths within a given folder

    Args:
        folder (str): The path to the folder
    Returns:
        file_paths (list): The list of file paths
    """

    file_paths = []

    for root, _, files in os.walk(folder):
        for file in files:
            file_paths.append(os.path.join(root, file))

    return file_paths

async def generate_random_string(length: int) -> str:
    """
    Generates a random string of uppercase letters and digits.

    Args:
        length (int): Length of the generated string
    Returns:
        str: The generated random string
    """

    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length)).replace("0", "O")

async def overlay_texture(image_path: str) -> str:
    # Choose a random texture file from the specified folder
    texture_path = await utils.choose_random_file(os.path.join(config.Paths.assets_folder, "Captcha Textures"))
    
    # Open the image and texture files
    image = Image.open(image_path).convert("RGBA")
    texture = Image.open(texture_path).convert("RGBA")
    
    # Ensure the texture has the same resolution as the image
    texture = texture.resize(image.size)
    
    # Randomize the opacity of the texture
    opacity = random.randint(20, 63)
    texture = texture.copy()
    texture.putalpha(opacity)
    
    # Overlay the texture onto the image
    combined = Image.alpha_composite(image, texture)
    
    # Save the result
    output_path = os.path.splitext(image_path)[0] + "_with_texture.png"
    combined.save(image_path)
    
    return output_path

async def generate_image(captcha_id: str) -> tuple:
    """
    Generates a captcha image.

    Args:
        captcha_id (str): UUID of the captcha
    Returns:
        path (str): The path of the generated image
        text (str): The generated string of the captcha
    """

    fonts = await get_all_file_paths("C:/Users/paul/OneDrive/Desktop/Coding/Discord Bots/DarkylAssistant/Assets/Fonts/captcha fonts")

    text = await generate_random_string(6)

    captcha: ImageCaptcha = ImageCaptcha(width=500,
                                         height=220,
                                         fonts=fonts,
                                         font_sizes=(40, 70, 100, 60, 80, 90))
    
    captcha_path = os.path.join(config.Paths.data_folder, "Generated Captchas", f"{captcha_id}.png")

    captcha.write(chars=text, output=captcha_path)

    await overlay_texture(captcha_path)

    return captcha_path, text
