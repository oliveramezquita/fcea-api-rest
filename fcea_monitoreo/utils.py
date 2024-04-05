from pymongo import MongoClient
from decouple import config


def _get_db_handle():
    MONGO_HOST = config('DATABASE_HOST')
    MONGO_PORT = config('DATABASE_PORT')
    MONGO_USER = config('DATABASE_USERNAME')
    MONGO_PASS = config('DATABASE_PASSWORD')

    uri = "mongodb://{}:{}@{}:{}?authSource=admin".format(
        MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT)
    client = MongoClient(uri)

    db_handle = client['fceadb']
    return db_handle


def _get_collection_handle(collection):
    db_handle = _get_db_handle()
    return _set_collection(db_handle, collection)


def _set_collection(db_handle, collection):
    return db_handle[collection]


def get_collection(collection, filter=None, sort_by=None, order_by=None):
    collection_handle = _get_collection_handle(collection)
    data = collection_handle.find(filter)

    if sort_by and order_by:
        if order_by == 'asc':
            data.sort(sort_by, 1)
        else:
            data.sort(sort_by, -1)

    return list(data)


def distinct_collection(collection, value):
    collection_handle = _get_collection_handle(collection)
    return list(collection_handle.distinct(value))


def insert_document(collection, data, filter=None):
    collection_handle = _get_collection_handle(collection)
    if collection_handle.find_one(filter):
        return False
    else:
        collection_handle.insert_one(data)
        return True


def update_document(collection, filter, update):
    collection_handle = _get_collection_handle(collection)
    collection_handle.update_one(filter, {'$set': update})
    return collection_handle.find_one(filter)
