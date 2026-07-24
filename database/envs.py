import logging
from struct import pack
import re
import base64
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.errors import PyMongoError
from datetime import datetime
import hashlib
from pymongo.errors import PyMongoError
from pymongo import UpdateOne
import hashlib
import json
from datetime import datetime
from info import FILE_DB_URI
# Function to generate a unique batch ID (e.g., BATCH-XXXXXXXXXX-01)
from pymongo import MongoClient
from datetime import datetime
import hashlib
import logging

DATABASE_NAME1 = "database_name"
COLLECTIONB_NAME1 = "env_config"
# Ensure that MongoDB client and collections are initialized properly
#client = MongoClient(FILE_DB_URI1)
#db = client[DATABASE_NAME1]
#col = db[COLLECTIONB_NAME1]
##
from pymongo.errors import ConnectionFailure, ConfigurationError
from pymongo.errors import PyMongoError

try:
    # MongoDB connection setup
    client = MongoClient(FILE_DB_URI)

    # Accessing the database
    db = client[DATABASE_NAME1]

    # Accessing a specific collection
    col = db[COLLECTIONB_NAME1]

    print("Connected to MongoDB successfully.")

except ConnectionFailure as e:
    # Handle connection-related errors
    print(f"Failed to connect to MongoDB: {e}")
except ConfigurationError as e:
    # Handle configuration-related errors
    print(f"MongoDB configuration error: {e}")
except Exception as e:
    # Handle any other unforeseen errors
    print(f"An unexpected error occurred: {e}")


# Configure logger
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.StreamHandler(),  # Output logs to console
        logging.FileHandler("app.log")  # Output logs to a file named 'app.log'
    ]
)

# Create logger
logger = logging.getLogger(__name__)


# Fetch configuration from MongoDB
def fetch_config(config_name):
    """Fetch configuration from MongoDB or return empty dict if not found."""
    try:
        config = col.find_one({"config_name": config_name})
        if config:

            #logger.info(f"Configuration {config_name} & config: {config}  fetched successfully.")
            return config
        else:
            logger.warning(f"Configuration {config_name} & config: {config} not found in database. Using default values.")
            return {}  # Return an empty dict if the config is not found
    except Exception as e:
        logger.error(f"Error fetching {config_name} configuration: {e}")
        return {}


def save_env(config_name, key, value):
    """Save the environment variable to MongoDB."""
    try:
        col.update_one(
            {"config_name": config_name},
            {"$set": {key: value}},
            upsert=True
        )
        print(f"Environment variable {key} saved successfully under {config_name}.")
    except Exception as e:
        print(f"Error saving environment variable: {e}")

def get_env(config_name):
    """Retrieve the environment configuration from MongoDB."""
    try:
        config = col.find_one({"config_name": config_name})
        if config:
            return config
        else:
            return {}
    except Exception as e:
        print(f"Error fetching environment configuration: {e}")
        return {}



def fetch_all_configs():
    """Fetch all environment configurations from MongoDB."""
    try:
        configs = col.find()
        return list(configs)
    except Exception as e:
        # logging.error(f"Error fetching all configurations: {e}")
        return []



async def update_config(config_name, key, value):
    """
    Update a specific key-value pair in the environment configuration.
    """
    try:
        # Find the configuration document by config_name
        config_data = col.find_one({"config_name": config_name})

        if config_data:
            # Update the key-value pair
            col.update_one(
                {"config_name": config_name},
                {"$set": {key: value}}  # Update the value of the key
            )
            logger.info(f"Updated {key} to {value} in config {config_name}")
            return True
        else:
            # If config_name doesn't exist, create it
            col.insert_one({
                "config_name": config_name,
                key: value
            })
            logger.info(f"Created new config {config_name} with {key}={value}")
            return True
    except Exception as e:
        logger.error(f"Error while updating config: {e}")
        return False

def delete_env_from_db(config_name: str, key: str) -> bool:
    """
    Deletes an environment variable from a specified config in the database.

    Args:
        config_name (str): The name of the config.
        key (str): The key of the environment variable to delete.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    try:
        # Ensure the config exists
        config_data = col.find_one({"config_name": config_name})
        if not config_data:
            print(f"No config found with name: {config_name}")
            return False

        # Perform the deletion
        result = col.update_one(
            {"config_name": config_name},
            {"$unset": {key: ""}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error while deleting environment variable: {e}")
        return False
