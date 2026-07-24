from pyrogram import Client, filters
from info import *
#bot = Client("my_bot")
from database.envs import fetch_config, get_env, save_env, fetch_all_configs, update_config, delete_env_from_db
from database.users_chats_db import db
from pyrogram.types import Message
from pymongo import UpdateOne
import logging
from pyrogram.enums import ParseMode
from langs.i18n import get, DEFAULT_LANG
# Set up logger
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message(filters.command('add_env') & filters.user(ADMINS))  # Replace with admin IDs
async def add_env(client, message):
    lang = await _user_lang(message.from_user)
    args = message.text.split()
    if len(args) < 3:
        await message.reply(get(lang, "ENV_ADD_USAGE"))
        return

    config_name, key, value = args[1], args[2], " ".join(args[3:])

    save_env(config_name, key, value)  # Save the environment variable to the DB
    if DEBUG_MODE:
        logger.info("[ENV] /add_env: saved | config=%s key=%s admin_id=%s", config_name, key, message.from_user.id)
    await message.reply(get(lang, "ENV_ADD_SUCCESS", key=key, value=value, config_name=config_name), parse_mode=ParseMode.HTML)

@Client.on_message(filters.command('get_envs') & filters.user(ADMINS))  # Replace with admin IDs
async def get_envs(client, message):
    lang = await _user_lang(message.from_user)
    args = message.text.split()
    if len(args) < 2:
        await message.reply(get(lang, "ENV_GET_USAGE"))
        return

    config_name = args[1]
    env_data = get_env(config_name)

    if not env_data:
        if DEBUG_MODE:
            logger.info("[ENV] /get_envs: no data | config=%s admin_id=%s", config_name, message.from_user.id)
        await message.reply(get(lang, "ENV_GET_EMPTY", config_name=config_name))
    else:
        env_str = "\n\n".join([f"{key} = {value}" for key, value in env_data.items()])
        await message.reply(get(lang, "ENV_GET_LIST", config_name=config_name, env_str=env_str), parse_mode=ParseMode.HTML)

@Client.on_message(filters.command("all_envs") & filters.user(ADMINS))
async def envs_command(client: Client, message: Message):
    """
    Handle the /envs command to fetch and display all environment configurations.
    """
    lang = await _user_lang(message.from_user)
    try:
        # Fetch all configurations
        configs = fetch_all_configs()

        if configs:
            response = get(lang, "ENV_ALL_HEADER")
            for config in configs:
                config_name = config.get("config_name", "Unknown")

                # Clean the config name just in case
                config_name = str(config_name).encode('utf-8', 'ignore').decode('utf-8')

                details_list = []
                for key, value in config.items():
                    if key != "_id":
                        # Convert both key and value to string, then scrub surrogate characters
                        clean_key = str(key).encode('utf-8', 'ignore').decode('utf-8')
                        clean_value = str(value).encode('utf-8', 'ignore').decode('utf-8')
                        details_list.append(f"{clean_key} = {clean_value}")

                details = "\n\n".join(details_list)
                response += get(lang, "ENV_ALL_ITEM", config_name=config_name, details=details)

            if DEBUG_MODE:
                logger.info("[ENV] /all_envs: listed | count=%s admin_id=%s", len(configs), message.from_user.id)
            # Send the formatted response
            await message.reply(response)
        else:
            await message.reply(get(lang, "ENV_ALL_EMPTY"))

    except Exception as e:
        # Clean the error message too, just in case 'e' contains the bad character
        clean_err = str(e).encode('utf-8', 'ignore').decode('utf-8')
        logger.exception(e)
        await message.reply(get(lang, "ENV_ALL_ERROR", error=clean_err))


@Client.on_message(filters.command('update_env') & filters.user(ADMINS))  # Only admins can use this
async def update_env(client, message):
    lang = await _user_lang(message.from_user)
    args = message.text.split()

    if len(args) < 4:
        await message.reply(get(lang, "ENV_UPDATE_USAGE"))
        return

    config_name = args[1]
    key = args[2]
    value = " ".join(args[3:])  # In case value has spaces

    # Update the environment variable in the DB
    success = await update_config(config_name, key, value)

    if DEBUG_MODE:
        logger.info("[ENV] /update_env: %s | config=%s key=%s admin_id=%s", "success" if success else "failed", config_name, key, message.from_user.id)

    if success:
        await message.reply(get(lang, "ENV_UPDATE_SUCCESS", key=key, value=value, config_name=config_name))
    else:
        await message.reply(get(lang, "ENV_UPDATE_FAIL", key=key, config_name=config_name))

@Client.on_message(filters.command('delete_env') & filters.user(ADMINS))  # Replace with admin IDs
async def delete_env(client, message):
    lang = await _user_lang(message.from_user)
    args = message.text.split()
    if len(args) < 3:
        await message.reply(get(lang, "ENV_DELETE_USAGE"))
        return

    config_name, key = args[1], args[2]

    # Attempt to delete the environment variable
    success = delete_env_from_db(config_name, key)  # Function to delete the key from DB
    if DEBUG_MODE:
        logger.info("[ENV] /delete_env: %s | config=%s key=%s admin_id=%s", "success" if success else "failed", config_name, key, message.from_user.id)
    if success:
        await message.reply(get(lang, "ENV_DELETE_SUCCESS", key=key, config_name=config_name), parse_mode=ParseMode.HTML)
    else:
        await message.reply(get(lang, "ENV_DELETE_FAIL", key=key, config_name=config_name), parse_mode=ParseMode.HTML)
