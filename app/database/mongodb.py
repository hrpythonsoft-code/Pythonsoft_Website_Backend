from pymongo import AsyncMongoClient

from app.core.config import settings


client = AsyncMongoClient(settings.MONGODB_URL)

database = client[settings.DB_NAME]


# Collections
admins_collection = database["admins"]
courses_collection = database["courses"]
batches_collection = database["batches"]



async def connect_to_mongodb():
    try:
        await client.admin.command("ping")

        print("MongoDB Atlas connected successfully")


    except Exception as error:
        print(f"MongoDB connection failed: {error}")
        raise


async def close_mongodb_connection():
    await client.close()
    print("MongoDB connection closed")