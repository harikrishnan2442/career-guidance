from pymongo import MongoClient

class MongoDBHelper:
    def __init__(self, connection_string, db_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]

    def insert_document(self, collection_name, document):
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id

    def find_document(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find_one(query)

    def update_document(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.update_one(query, {'$set': new_values})
        return result.modified_count

    def delete_document(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count
    
    def aggregate(self, collection_name, pipeline):
        collection = self.db[collection_name]
        return collection.aggregate(pipeline)