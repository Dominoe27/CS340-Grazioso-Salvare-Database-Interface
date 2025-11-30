from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os

# Grab the MongoDB port from the environment if it exists,
# otherwise use a default port. Makes the project easier to run anywhere.
MONGO_PORT = int(os.getenv("MONGO_PORT", 31580))


class AnimalShelter(object):
    """CRUD operations for the Animal collection in MongoDB."""

    def __init__(self, host, dbname, username, password):
        """
        Set up the Mongo client and connect to the database.
        Credentials and host can come from env variables so nothing
        sensitive is hardcoded. Keeps the project cleaner and safer.
        """
        uri = (
            f"mongodb://{username}:{password}"
            f"@{host}:{MONGO_PORT}/{dbname}?authSource=admin"
        )

        try:
            self.client = MongoClient(uri)
            self.database = self.client[dbname]
            # Animals collection is the main one used in this project.
            self.collection = self.database["animals"]
        except PyMongoError as e:
            # If we can't connect, fail early so the dashboard isn't guessing.
            raise ConnectionError(f"Could not connect to MongoDB: {e}")

    def _validate_dict_input(self, value, name):
        """
        Quick helper to keep inputs sane.
        Everything coming into CRUD should be a dict.
        I check this once here instead of rewriting it everywhere else.
        """
        if not isinstance(value, dict):
            raise ValueError(f"{name} must be a dictionary.")
        return value

    def create(self, data):
        """
        Insert a single document. Pretty straightforward.
        I return True or False so the calling code knows exactly what happened.
        """
        self._validate_dict_input(data, "data")

        if not data:
            raise ValueError("data cannot be empty for create.")

        try:
            self.collection.insert_one(data)
            return True
        except PyMongoError as e:
            print(f"Insert failed: {e}")
            return False

    def read(self, query):
        """
        Read documents from the animals collection.

        Allowing {} here is intentional. The dashboard needs to load
        all animals on startup, so I let Mongo handle {} as 'return everything.'
        """
        if query is None:
            raise ValueError("query cannot be None for read.")

        self._validate_dict_input(query, "query")

        try:
            results = list(self.collection.find(query))
            return results
        except PyMongoError as e:
            print(f"Read failed: {e}")
            return []

    def update(self, query, update_data):
        """
        Update documents that match the query.

        For safety, query cannot be empty. I do not want someone to
        accidentally update the entire database with one bad call.
        """
        self._validate_dict_input(query, "query")
        self._validate_dict_input(update_data, "update_data")

        if not query:
            raise ValueError("query cannot be empty for update.")

        if not update_data:
            raise ValueError("update_data cannot be empty for update.")

        try:
            result = self.collection.update_many(query, {"$set": update_data})
            return result.modified_count
        except PyMongoError as e:
            print(f"Update failed: {e}")
            return 0

    def delete(self, query):
        """
        Delete documents that match the query.

        Same safety rule here. No empty queries.
        This prevents deleting the entire collection by mistake.
        """
        self._validate_dict_input(query, "query")

        if not query:
            raise ValueError("query cannot be empty for delete.")

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print(f"Delete failed: {e}")
            return 0
