import motor.motor_asyncio
from bson import ObjectId
from decouple import config
from typing import Optional

MONGO_DETAILS = config('MONGO')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client['fimi']