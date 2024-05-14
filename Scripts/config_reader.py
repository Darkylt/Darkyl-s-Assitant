import yaml
import os

CONFIG_FILENAME = "config.yml"
SECRET_FILENAME = "secret.yml"

config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILENAME)

secret_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), SECRET_FILENAME)

try:
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    raise Exception("Configuration file not found. Please make sure the config.yml file is in the Main Folder.")
except yaml.YAMLError:
    raise Exception("Error parsing the configuration file. Invalid YAML format. Please make sure the config.yml is formatted correctly.")

try:
    with open(secret_path, encoding="utf-8") as f:
        secret = yaml.safe_load(f)
except FileNotFoundError:
    raise Exception("Configuration file not found. Please make sure the secret.yml file is in the Main Folder.")
except yaml.YAMLError:
    raise Exception("Error parsing the configuration file. Invalid YAML format. Please make sure the secret.yml is formatted correctly.")

class Bot:
    token = secret["Bot Token"]
    server = config["Server ID"]
    root_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    logs_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "logs")
    data_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Data")
    assets_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Assets")
    darkyl_id = config["Darkyl User ID"]
    verified_role = config["Verified Role"]
    logs_channel = config["Logs Channel"]
    random_tips = config["Random Tips Enabled"]
    random_tips_channel = config["Random Tips Channel"]
    admin_role = config["Admin Role"]
    mod_role = config["Moderator Role"]
    report_channel = config["Reports Channel"]
    censored_words = config["Censored Words"]
    level_update_channel = config["Level Channel"]
    level_updates_enabled = config["Level Updates"]
    worm_is_running = False
    

class Join:
    overlay_path = os.path.join(Bot.assets_folder, "Welcome Image.png")
    channel = config["Welcome Channel"]
    welcome_card_scale_factor = config["Scale Factor"]

class ReactionRoles:
    gamer_role = config["Gamer Role"]
    musician_role = config["Musician Role"]
    dj_role = config["DJ Role"]
    photographer_role = config["Photographer Role"]
    content_creator_role = config["Content Creator Role"]
    visual_artist_role = config["Visual Artist Role"]
    he_him_role = config["he/him Role"]
    she_her_role = config["she/her Role"]
    they_them_role = config["they/them Role"]
    other_ask_role = config["other (ask) Role"]
    north_america_role = config["North America Role"]
    south_america_role = config["South America Role"]
    europe_role = config["Europe Role"]
    asia_role = config["Asia Role"]
    africa_role = config["Africa Role"]
    oceania_australia_role = config["Oceania/Australia Role"]
    skibidy_toilet_role = config["Skibidy Toilet Role"]
    youtube_ping_role = config["YouTube Ping Role"]

class YouTube:
    ping_role = config["YouTube Ping Role"]
    api_key = secret["YouTube API Key"]
    channel = config["YouTube Channel"]
    last_uploaded_video_file = os.path.join(Bot.data_folder, "last_uploaded_video.txt")
    provided_check_frequency = config["YouTube Check Frequency"]
    check_frequency = 3600
    discord_channel = config["YouTube Discord Channel"]

class HelpMessage:
    message = config["Help Message"]
    message_all = config["Help Message All commands"]
    message_all_admin = config["Help Message Admin commands"]
    message_fun = config["Help Message Fun commands"]
    message_utility = config["Help Message Utility commands"]
    rules = config["Rules Discord"]
    rules_vc =  config["Rules VC"]
    scam_message = config["Scams"]

class AutoMod:
    filter_nsfw_language = config["Filter NSFW Words"]
    allowed_files = config["Allowed Files"]

class Level:
    leve_from_xp_mapping = config["Level From XP"]

class Stats:
    api_key = secret["Tracker.gg API Key"]

class InvalidConfigError(Exception):
    pass

def validate():
    """
    Checks from a list of required keys and their types if the config is valid.
    """ # Note: Add other validation checks later

    required_keys = {
        "Server ID": int,
        "Darkyl User ID": int,
        "Logs Channel": int,
        "Welcome Channel": int,
        "Scale Factor": float,
        "Verified Role": int,
        "Gamer Role": int,
        "Musician Role": int,
        "DJ Role": int,
        "Photographer Role": int,
        "Content Creator Role": int,
        "Visual Artist Role": int,
        "he/him Role": int,
        "she/her Role": int,
        "they/them Role": int,
        "other (ask) Role": int,
        "North America Role": int,
        "South America Role": int,
        "Europe Role": int,
        "Asia Role": int,
        "Africa Role": int,
        "Oceania/Australia Role": int,
        "Skibidy Toilet Role": int,
        "YouTube Ping Role": int,
        "YouTube Discord Channel": int,
        "YouTube Channel": str,
        "YouTube Check Frequency": int,
        "Random Tips Enabled": bool,
        "Random Tips Channel": int,
        "Admin Role": int,
        "Reports Channel": int,
        "Help Message": str,
        "Help Message All commands": str,
        "Help Message Admin commands": str,
        "Help Message Fun commands": str,
        "Moderator Role": int,
        "Censored Words": list,
        "Level From XP": dict,
        "Level Channel": int,
        "Level Updates": bool,
        "Filter NSFW Words": bool,
        "Allowed Files": list
    }

    for key, expected_type in required_keys.items():
        if key not in config:
            raise InvalidConfigError(f"Key '{key}' in config.yml is missing.")
        if isinstance(expected_type, tuple):
            expected_types = [t.__name__ for t in expected_type]
            expected_types_str = " or ".join(expected_types)
            if not any(isinstance(config[key], t) for t in expected_type):
                raise InvalidConfigError(f"Key '{key}' in config.yml is supposed to be {expected_types_str}.")
        else:
            if not isinstance(config[key], expected_type):
                raise InvalidConfigError(f"Key '{key}' in config.yml is supposed to be a {expected_type.__name__}.")

    YouTube.check_frequency = YouTube.provided_check_frequency