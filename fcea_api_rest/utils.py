from pymongo import MongoClient


def _get_db_handle():
    client = MongoClient(
        host='127.0.0.1',
        port=int(27017),
        username='root',
        password='root'
    )
    db_handle = client['fceadb']
    return db_handle


def _get_collection_handle(collection):
    db_handle = _get_db_handle()
    return _set_collection(db_handle, collection)


def _set_collection(db_handle, collection):
    collist = db_handle.list_collection_names()
    return db_handle[collection]


def insert_document(collection, data):
    collection_handle = _get_collection_handle(collection)
    if collection_handle.find_one({'_id': data['_id']}):
        pass
    else:
        collection_handle.insert_one(data)
