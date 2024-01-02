# arango_datasets
Package for loading example datasets into an ArangoDB Instance.

```py
from arango import ArangoClient
from arango_datasets import Datasets

# Datasets requires a valid database object 
db = ArangoClient(hosts='http://localhost:8529').db("dbName", username="root", password="")

datasets = Datasets(db)

# List available datasets
datasets.list_datasets()

# List more information about a particular dataset
datasets.dataset_info("IMDB_X")

# Import the dataset
datasets.load("IMDB_X")
```