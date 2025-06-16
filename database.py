"""
Database class containing associated functions, and instantiation of Database object
"""
from pymongo import MongoClient
from libs.utils import config
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("db")


class Database:
    """
    A class to perform all database related operations
    """

    def create_connection(self):
        """
        Establishes a connection to the MongoDB database and returns the database object.

        Returns:
            pymongo.database.Database: The MongoDB database object.
        """
        try:
            client = MongoClient(config.DB_URL)
            database = client[config.DB_NAME]
            logger.info("Connected to DB!")
            return database
        except Exception as e:
            logger.error(f"Error establishing connection to Database: {str(e)}")
            return None

    def get_or_create_collection(self, collection_name):
        """
        Retrieves an existing MongoDB collection or creates a new one if it doesn't exist.

        Args:
            collection_name (str): The name of the collection to retrieve or create.

        Returns:
            pymongo.collection.Collection or None: The MongoDB collection object if successful, 
            or None if an error occurred.
        """

        try:
            database = self.create_connection()
            if collection_name in database.list_collection_names():
                logger.info(f"Fetched collection: {collection_name}")
                collection = database[collection_name]
            else:
                logger.info(f"Created collection: {collection_name}")
                collection = database.create_collection(collection_name)
            return collection
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return None

    def insert_data(self, collection_name, data, validator=None, indexes=None):
        """
        Inserts the given data into the specified MongoDB collection.
        
        Args:
            collection_name (str): The name of the MongoDB collection to insert the data into.
            data (list): The data to insert into the collection.

        """
        try:
            database = self.create_connection()
            collection = self.get_or_create_collection(collection_name)

            # Apply validator if provided
            if validator:
                try:
                    database.command("collMod", collection_name, validator=validator)
                    logger.info(f"Applied validator for collection: {collection_name}")
                except Exception as e:
                    # If collMod fails because the collection
                    # doesn't exist, create it with the validator
                    if "cannot be modified" in str(e):
                        database.create_collection(collection_name, validator=validator)
                        logger.info(f"Created collection with validator: {collection_name}")
                    else:
                        logger.error(f"Error applying validator: {str(e)}")

            # Create indexes if provided
            if indexes:
                for index in indexes:
                    field = index["field"]
                    unique = index.get("unique", False)
                    collection.create_index(field, unique=unique)
                    logger.info(f"Created index on '{field}' "
                                f"(unique={unique}) for collection: {collection_name}")

            # db.command("collMod", collection_name, validator=vendor_validator)
            ids = collection.insert_many(data)
            logger.info(f"Inserted {len(ids.inserted_ids)} documents into collection: {collection}")
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")

    def update_data(self, collection_name, filter_query, data, upsert=False, multiple=False):
        """
        Update data in given collection
        :param collection_name: The name of the connection.
        :param filter_query: The query for filtering records while updating
        :param data: The data to update
        :param upsert: Flag to indicate whether to insert the record if it doesn't already exist
        :param multiple: Flag to indicate whether to update multiple records
        :return: dictionary containing counts of matched and updated results.
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            if multiple:
                result = collection.update_many(filter_query, data, upsert=upsert)
                logger.info(f"Updated {result.modified_count} documents "
                            f"(matched {result.matched_count}) in collection: {collection_name}")
            else:
                result = collection.update_one(filter_query, data, upsert=upsert)
                logger.info(f"Updated {result.modified_count} document "
                            f"(matched {result.matched_count}) in collection: {collection_name}")

            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
            }
        except Exception as e:
            logger.error(f"Error updating data in collection {collection_name}: {str(e)}")
            return None

    def bulk_write_data(self, collection_name, operations):
        """
        Perform bulk write operations in a collection.

        Args:
            collection_name (str): The name of the collection.
            operations (list): A list of UpdateOne, UpdateMany, or other bulk operations.

        Returns:
            dict: The result of the bulk write operation.
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            # Perform bulk write
            result = collection.bulk_write(operations)
            logger.info(f"Bulk write completed: Matched {result.matched_count}, "
                        f"Modified {result.modified_count}")

            response = {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_count": len(result.upserted_ids) if result.upserted_ids else 0,
            }
            return response
        except Exception as e:
            logger.error(f"Error performing bulk write in collection {collection_name}: {str(e)}")
            return None

    def drop_collection(self, collection_name):
        """
        Drops the collection if given collection name exists.

        Args:
            collection_name (str): The name of the MongoDB collection to be dropped.

        """
        try:
            database = self.create_connection()
            collections = database.list_collection_names()
            if collection_name in collections:
                logger.info(f"Dropping {collection_name} collection")
                database.drop_collection(collection_name)
            else:
                logger.error(f"Collection {collection_name} does not exists.")
        except Exception as e:
            logger.error(f"Error dropping collection: {str(e)}")


db = Database()
