import config_reader as config
import vars


async def update_captcha_status():
    if config.Verification.disable_captcha:
        vars.captcha_enabled = False
        return

    if config.Verification.force_captcha:
        vars.captcha_enabled = True
        return

    if vars.raid:
        vars.captcha_enabled = True
        return

    vars.captcha_enabled = False
