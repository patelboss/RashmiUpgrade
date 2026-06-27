# database/verified.py

from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz

# Initialize MongoDB client and database (replace with your connection details)
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']  # replace 'your_database' with your actual database name
verified_collection = db['verified_users']

async def check_verification(userid):
    """
    Check if the user is verified within the last 24 hours.
    Returns True if verified, else False.
    """
    verified_user = await verified_collection.find_one({'user_id': userid})

    if verified_user:
        # Check if the verification is within the last 24 hours
        verification_time = verified_user['verified_at']
        if verification_time + timedelta(hours=24) > datetime.utcnow():
            return True  # Verified within the last 24 hours
        else:
            # Remove expired verification
            await verified_collection.delete_one({'user_id': userid})
            return False  # Expired verification
    else:
        return False  # User not verified

async def verify_user(userid):
    """
    Save the user's verification status with the current timestamp.
    """
    verified_data = {
        'user_id': userid,
        'verified_at': datetime.utcnow()  # Store the current UTC time for verification
    }

    # Insert or update the user's verification status in MongoDB
    await verified_collection.update_one(
        {'user_id': userid},
        {'$set': verified_data},
        upsert=True  # Create the document if it doesn't exist
    }

async def remove_expired_verification(userid):
    """
    Remove expired verification (older than 24 hours) from the database.
    """
    await verified_collection.delete_one({'user_id': userid})
