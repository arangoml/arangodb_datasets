# arango_datasets
Package for loading example datasets into an ArangoDB Instance.

```py
# pip install arango-datasets

from arango import ArangoClient
from arango_datasets import Datasets

# Datasets requires a valid database object 
db = ArangoClient(hosts='http://localhost:8529').db("dbName", username="root", password="")

datasets = Datasets(db)

# List available datasets
print(datasets.list_datasets())

# List more information about a particular dataset
print(datasets.dataset_info("IMDB_X"))

# Import the dataset
datasets.load("IMDB_X")
```
