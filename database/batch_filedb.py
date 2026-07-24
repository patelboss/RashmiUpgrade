import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from info import DATABASE_URI, DATABASE_NAME
from utils import get_settings, save_group_settings
from pymongo.errors import PyMongoError
from datetime import datetime
import hashlib
from pymongo.errors import PyMongoError
from pymongo import UpdateOne
import hashlib
import json
from datetime import datetime

# Function to generate a unique batch ID (e.g., BATCH-XXXXXXXXXX-01)
from pymongo import MongoClient
from datetime import datetime
import hashlib
import logging

COLLECTIONB_NAME = "Batched"
# Ensure that MongoDB client and collections are initialized properly
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
col = db["batch"]

logger = logging.getLogger(__name__)

# Function to generate a unique batch ID (e.g., BATCH-XXXXXXXXXX-01)
def generate_batch_id():
    """
    Generates a unique batch ID using a timestamp, hash, and sequence number.

    Returns:
        str: The generated batch ID.
    """
    try:
        # Generate a unique timestamp for the batch ID
        current_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
#        logger.debug(f"Generated timestamp for batch ID: {current_timestamp}")

        # Generate a hash from the timestamp
        hash_part = hashlib.sha256(current_timestamp.encode()).hexdigest()[:10]
#        logger.debug(f"Generated hash part for batch ID: {hash_part}")

        # Get the latest sequence number and increment it
        sequence_number = get_latest_batch_sequence() + 1
#        logger.info(f"Retrieved and incremented sequence number for batch ID: {sequence_number}")

        # Combine the components to create the batch ID
        batch_id = f"Filmykeedha-{hash_part}-{str(sequence_number).zfill(2)}"
#        logger.info(f"Generated batch ID: {batch_id}")

        return batch_id
    except Exception as e:
        logger.error(f"Error generating batch ID: {str(e)}")
        raise  # Re-raise to allow higher-level handling

# Function to get the latest batch sequence number (for uniqueness)
def get_latest_batch_sequence():
    """
    Retrieves the latest sequence number for batch IDs from the database.

    Returns:
        int: The latest sequence number, or 0 if none exists.
    """
    try:
        latest_batch = col.find_one(sort=[("created_at", -1)])  # Sort by most recent entry
        if latest_batch and "batch_id" in latest_batch:
            # Extract sequence number from batch ID (last component after the second dash)
            sequence_number = int(latest_batch["batch_id"].split("-")[-1])
#            logger.debug(f"Latest sequence number retrieved: {sequence_number}")
            return sequence_number
        return 0  # No existing batches found
    except PyMongoError as e:
        logger.error(f"Database error retrieving latest batch sequence: {str(e)}")
        raise Exception(f"Database error: {e}")  # Re-raise for handling
    except Exception as e:
        logger.error(f"Unexpected error retrieving latest batch sequence: {str(e)}")
        raise  # Re-raise for further handling
# Function to save batch details to the database

async def save_batch_details(file_data, batch_name, optional_message=None):
    """
    Saves the batch details to the database and returns the generated batch ID.

    Args:
        file_data (list): List of file metadata for the batch.
        batch_name (str): Name of the batch.
        optional_message (str, optional): Additional message provided by the user.

    Returns:
        str: The generated batch ID.
    """
    try:
        # Generate a unique batch ID
        batch_id = generate_batch_id()
#        logger.info(f"Generated batch ID: {batch_id}")

        # Prepare batch details
        batch_details = {
            "batch_id": batch_id,
            "file_data": file_data,
            "batch_name": batch_name,
            "optional_message": optional_message if optional_message else "No message provided",
            "created_at": datetime.utcnow()
        }
#        logger.debug(f"Batch details prepared: {batch_details}")

        # Save batch details in the main collection
        col.insert_one(batch_details)
#        logger.info(f"Batch {batch_id} saved successfully with name '{batch_name}'")

        return batch_id  # Return the generated batch ID
    except PyMongoError as e:
        logger.error(f"Database error saving batch {batch_id}: {str(e)}")
        raise Exception(f"Database error: {e}")  # Re-raise for higher-level handling
    except Exception as e:
        logger.error(f"Unexpected error saving batch {batch_id}: {str(e)}")
        raise  # Re-raise for further handling

async def get_batch_by_id(batch_id):
    """
    Retrieve batch details from the database using batch_id.

    :param batch_id: The unique ID of the batch to retrieve.
    :return: A dictionary containing batch details if found, otherwise None.
    """
    try:
        # Log the batch_id to ensure it is correct
#        logger.info(f"Attempting to retrieve batch with ID: {batch_id}")

        # Create an index on batch_id for faster lookups (this can be run separately to ensure index is created)
        col.create_index("batch_id")

        # Query the database for the batch
        batch_details = col.find_one({"batch_id": batch_id})

        # Log the raw result from the query to see what is being returned
 #       logger.info(f"Retrieved batch details: {batch_details}")

        if batch_details:
 #           logger.info(f"Batch {batch_id} found in the database. Details: {batch_details}")
            return batch_details
        else:
 #           logger.warning(f"Batch {batch_id} not found in the database.")
            return None

    except PyMongoError as e:
        # Log any errors that occur during the query process
 #       logger.error(f"Error retrieving batch {batch_id} from the database: {str(e)}")
        return None
import asyncio

async def fetch_file_by_link(batch_id: str, unique_link: str):
    """
    Fetch a file from the database using the batch ID and unique link.

    Args:
        batch_id (str): The ID of the batch.
        unique_link (str): The unique identifier for the specific file.

    Returns:
        dict: File metadata if found, None otherwise.
    """
    from pymongo.errors import PyMongoError

#    logger.info("Starting fetch_file_by_link process...")
#    await asyncio.sleep(3)

    # Log the batch ID and unique link
#    logger.info("Batch ID provided: %s", batch_id)
#    await asyncio.sleep(3)
#    logger.info("Unique Link provided: %s", unique_link)
#    await asyncio.sleep(3)

    try:
        # Fetch the batch details from the database
#        logger.info("Attempting to retrieve batch with ID: %s", batch_id)
#        await asyncio.sleep(3)
        batch_metadata = col.find_one({"batch_id": batch_id})

        if not batch_metadata:
#            logger.error("Batch not found for batch ID: %s", batch_id)
            return None

#        logger.info("Batch found for batch ID: %s", batch_id)
#        await asyncio.sleep(3)
#        logger.info("Batch metadata: %s", batch_metadata)
#        await asyncio.sleep(3)

        # Search for the file within the batch using the unique link
#        logger.info("Searching for file with unique link: %s", unique_link)
#        await asyncio.sleep(3)
        file_metadata = next(
            (file for file in batch_metadata.get("file_data", []) if file.get("unique_link") == unique_link),
            None
        )

        if not file_metadata:
#            logger.error("File not found for unique link: %s in batch ID: %s", unique_link, batch_id)
            return None

#        logger.info("File found: %s", file_metadata)
#        await asyncio.sleep(3)
        return file_metadata

    except PyMongoError as e:
        logger.exception("Database error occurred: %s", str(e))
        return None

    except Exception as e:
        logger.exception("Unexpected error in fetch_file_by_link: %s", str(e))
        return None
