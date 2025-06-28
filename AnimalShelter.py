from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# MongoDB port — pulled from env or default
MONGO_PORT = int(os.getenv('MONGO_PORT', 31580))  # default port if env var not set

class AnimalShelter(object):
    """CRUD operations for the Animal collection in MongoDB"""

    def __init__(self, host, dbname, username, password):
        # Connect to MongoDB using dynamic credentials
        self.client = MongoClient(f'mongodb://{username}:{password}@{host}:{MONGO_PORT}/{dbname}?authSource=admin')
        self.database = self.client[dbname]
        self.collection = self.database['animals']  # Still the same collection name

    def create(self, data):
        if data and isinstance(data, dict):
            try:
                self.collection.insert_one(data)
                return True
            except Exception as e:
                print(f"Insert fail: {e}")
                return False
        else:
            raise Exception("Bad input: data needs to be a dictionary and not empty.")

    def read(self, query):
        if query and isinstance(query, dict):
            try:
                results = list(self.collection.find(query))
                return results
            except Exception as e:
                print(f"Read fail: {e}")
                return []
        else:
            raise Exception("Bad input: query needs to be a dictionary and not empty.")

    def update(self, query, update_data):
        if query and update_data and isinstance(query, dict) and isinstance(update_data, dict):
            try:
                result = self.collection.update_many(query, {"$set": update_data})
                return result.modified_count
            except Exception as e:
                print(f"Update fail: {e}")
                return 0
        else:
            raise Exception("Bad input: query and update data must be dictionaries.")

    def delete(self, query):
        if query and isinstance(query, dict):
            try:
                result = self.collection.delete_many(query)
                return result.deleted_count
            except Exception as e:
                print(f"Delete fail: {e}")
                return 0
        else:
            raise Exception("Bad input: query needs to be a dictionary and not empty.")