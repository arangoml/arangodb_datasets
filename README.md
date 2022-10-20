# arango_datasets
Package for loading example datasets into an ArangoDB Instance.

```
from arango_datasets.datasets import Datasets
from arango import ArangoClient

# Datasets requires a valid database object 
db = ArangoClient(hosts='http://localhost:8529').db("dbName", username="root", password="")

datasets = Datasets(db)

# list available datasets
datasets.list_datasets()

# list more information about the dataset files and characteristics 
#datasets.dataset_info("IMDB_X")

# Import the dataset
# datasets.load("IMDB_X")
```