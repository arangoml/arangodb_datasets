# arango_datasets
Package for loading example datasets into an ArangoDB Instance.

```
from arango_datasets.importer import Importer
from arango import ArangoClient

# Importer requires a valid database object 
db = ArangoClient(hosts='http://localhost:8529').db("dbName", username="root", password="")

importer = Importer(db)

# list available datasets
importer.list_datasets()

# list more information about the dataset files and characteristics 
#importer.dataset_info("IMDB_X")

# Import the dataset
# importer.load("IMDB_X")
```