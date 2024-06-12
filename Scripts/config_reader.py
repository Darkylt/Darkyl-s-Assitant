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

class Paths:
    root_folder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    logs_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "logs")
    data_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Data")
    assets_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Assets")
    scripts_folder = os.path.join(root_folder, "Scripts")

class Bot:
    token = secret["Bot Token"]
    server = config["Server"]["server_id"]
    darkyl_id = config["Owner"]["darkyl_id"]
    verified_role = config["Roles"]["verified"]
    muted_role = config["Roles"]["muted"]
    logs_channel = config["Channels"]["logs"]
    random_tips = config["Random Tips"]["enabled"]
    random_tips_channel = config["Random Tips"]["channel"]
    admin_role = config["Roles"]["admin"]
    mod_role = config["Roles"]["moderator"]
    report_channel = config["Channels"]["reports"]
    censored_roast_words = config["Moderation"]["roast_api_censored_words"]
    level_update_channel = config["Level System"]["update_channel"]
    level_updates_enabled = config["Level System"]["update_levels"]
    worm_is_running = False

class Join:
    overlay_path = os.path.join(Paths.assets_folder, "Welcome Image.png")
    channel = config["Welcome Card"]["channel"]
    welcome_card_scale_factor = config["Welcome Card"]["scale_factor"]

class ReactionRoles:
    gamer_role = config["Roles"]["Descriptors"]["gamer"]
    musician_role = config["Roles"]["Descriptors"]["musician"]
    dj_role = config["Roles"]["Descriptors"]["dj"]
    photographer_role = config["Roles"]["Descriptors"]["photographer"]
    content_creator_role = config["Roles"]["Descriptors"]["content_creator"]
    visual_artist_role = config["Roles"]["Descriptors"]["visual_artist"]
    he_him_role = config["Roles"]["Pronouns"]["he_him"]
    she_her_role = config["Roles"]["Pronouns"]["she_her"]
    they_them_role = config["Roles"]["Pronouns"]["they_them"]
    other_ask_role = config["Roles"]["Pronouns"]["other_ask"]
    north_america_role = config["Roles"]["Regions"]["north_america"]
    south_america_role = config["Roles"]["Regions"]["south_america"]
    europe_role = config["Roles"]["Regions"]["europe"]
    asia_role = config["Roles"]["Regions"]["asia"]
    africa_role = config["Roles"]["Regions"]["africa"]
    oceania_australia_role = config["Roles"]["Regions"]["oceania_australia"]
    skibidy_toilet_role = config["Roles"]["Pronouns"]["skibidy_toilet"]
    youtube_ping_role = config["Roles"]["Pings"]["youtube"]

class Channels:
    admin = config["Channels"]["admin"]

class YouTube:
    ping_role = config["Roles"]["Pings"]["youtube"]
    api_key = secret["YouTube API Key"]
    channel = config["YouTube"]["channel_id"]
    last_uploaded_video_file = os.path.join(Paths.data_folder, "last_uploaded_video.txt")
    provided_check_frequency = config["YouTube"]["check_frequency"]
    check_frequency = 3600
    discord_channel = config["YouTube"]["discord_channel"]

class HelpMessage:
    message = config["Help Messages"]["general"]
    message_all = config["Help Messages"]["all_commands"]
    message_all_admin = config["Help Messages"]["admin_commands"]
    message_fun = config["Help Messages"]["fun_commands"]
    message_utility = config["Help Messages"]["utility_commands"]
    rules = config["Rules Discord"]
    rules_vc =  config["Rules VC"]
    scam_message = config["Scams"]

class AutoMod:
    filter_nsfw_language = config["Moderation"]["filter_nsfw_words"]
    allowed_files = config["Moderation"]["allowed_files"]
    kick_threshold = config["Moderation"]["Warnings"]["kick_threshold"]
    ban_threshold = config["Moderation"]["Warnings"]["ban_threshold"]

class Level:
    leve_from_xp_mapping = config["Level System"]["level_xp_mapping"]

class InvalidConfigError(Exception):
    pass

def validate():
    """
    Checks from a list of required keys and their types if the config is valid.
    """ # Note: Add other validation checks later

    required_keys = {
        "Server.server_id": int,
        "Owner.darkyl_id": int,
        "Channels.logs": int,
        "Channels.reports": int,
        "Welcome Card.scale_factor": float,
        "Welcome Card.channel": int,
        "Roles.admin": int,
        "Roles.moderator": int,
        "Roles.verified": int,
        "Roles.muted": int,
        "Roles.Descriptors.gamer": int,
        "Roles.Descriptors.musician": int,
        "Roles.Descriptors.dj": int,
        "Roles.Descriptors.photographer": int,
        "Roles.Descriptors.content_creator": int,
        "Roles.Descriptors.visual_artist": int,
        "Roles.Pronouns.he_him": int,
        "Roles.Pronouns.she_her": int,
        "Roles.Pronouns.they_them": int,
        "Roles.Pronouns.other_ask": int,
        "Roles.Pronouns.skibidy_toilet": int,
        "Roles.Regions.north_america": int,
        "Roles.Regions.south_america": int,
        "Roles.Regions.europe": int,
        "Roles.Regions.africa": int,
        "Roles.Regions.asia": int,
        "Roles.Regions.oceania_australia": int,
        "Roles.Pings.youtube": int,
        "YouTube.channel_id": str,
        "YouTube.check_frequency": int,
        "YouTube.discord_channel": int,
        "Random Tips.enabled": bool,
        "Random Tips.channel": int,
        "Level System.update_levels": bool,
        "Level System.update_channel": int,
        "Level System.level_xp_mapping": dict,
        "Moderation.allowed_files": list,
        "Moderation.filter_nsfw_words": bool,
        "Moderation.roast_api_censored_words": list,
        "Moderation.Warnings.kick_threshold": int,
        "Moderation.Warnings.ban_threshold": int,
        "Help Messages.general": str,
        "Help Messages.all_commands": str,
        "Help Messages.admin_commands": str,
        "Help Messages.fun_commands": str,
        "Help Messages.utility_commands": str
    }

    def get_nested_key(d, keys):
            for key in keys.split('.'):
                if key in d:
                    d = d[key]
                else:
                    raise InvalidConfigError(f"Key '{keys}' in config.yml is missing.")
            return d

    for key, expected_type in required_keys.items():
        value = get_nested_key(config, key)
        if isinstance(expected_type, tuple):
            expected_types = [t.__name__ for t in expected_type]
            expected_types_str = " or ".join(expected_types)
            if not any(isinstance(value, t) for t in expected_type):
                raise InvalidConfigError(f"Key '{key}' in config.yml is supposed to be {expected_types_str}.")
        else:
            if not isinstance(value, expected_type):
                raise InvalidConfigError(f"Key '{key}' in config.yml is supposed to be a {expected_type.__name__}.")

    YouTube.check_frequency = YouTube.provided_check_frequency

    required_paths = [
        secret_path,
        config_path,
        Paths.logs_folder,
        Paths.assets_folder,
        Paths.data_folder,
        Paths.scripts_folder,
        os.path.join(Paths.scripts_folder, "ext"),
        os.path.join(Paths.scripts_folder, "AutoMod"),
    ]

    for path in required_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path {path} couldn't be found")
