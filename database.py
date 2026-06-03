"""
Opens a motor client and exposes the profiles collection.
Routers will import profiles from this module
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from config import settings

_client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongodb_uri)
_db = _client[settings.mongodb_db_name]  # Access db
profiles: AsyncIOMotorCollection = _db["profiles"]  # Access collection
