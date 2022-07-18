import os
import pymongo


def get_collection(collection_name):
    uri = os.getenv("CONNECTION_URI")
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[os.getenv("DATABASE")]
    collection = db[collection_name]
    return collection
