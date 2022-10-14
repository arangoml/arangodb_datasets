from arango_datasets.importer import Importer
from arango import ArangoClient

#TODO: Add real tests

db = ArangoClient(hosts='http://localhost:8529').db("dbName", username="root", password="")

importer = Importer(db)
importer.list_datasets()
# importer.dataset_info("IMDB_X")
# importer.load("IMDB_X")
