
from config import MONGO_URL
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

mongo = MongoClient(MONGO_URL)

db = mongo.Ubot
