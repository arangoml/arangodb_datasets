import sys
from typing import Any, Dict, List, Optional

import requests
from arango.collection import StandardCollection
from arango.database import Database
from arango.exceptions import CollectionCreateError, DocumentInsertError
from requests import ConnectionError, HTTPError

from .utils import progress


class Datasets:
    """ArangoDB Example Datasets

    :param db: A python-arango database instance
    :type db: arango.database.Database
    :param batch_size:
        Optional batch size supplied to python-arango import_bulk function
    :type batch_size: int
    :param metadata_file: Optional URL for datasets metadata file
    :type metadata_file: str
    """

    def __init__(
        self,
        db: Database,
        batch_size: Optional[int] = None,
        metadata_file: str = "https://arangodb-dataset-library.s3.amazonaws.com/root_metadata.json",  # noqa: E501
    ):
        self.metadata_file: str = metadata_file
        self.metadata_contents: Dict[str, Any]
        self.batch_size = batch_size
        self.user_db = db
        if issubclass(type(db), Database) is False:
            msg = "**db** parameter must inherit from arango.database.Database"
            raise TypeError(msg)

        try:
            response = requests.get(self.metadata_file)
            response.raise_for_status()
            self.metadata_contents = response.json()
        except (HTTPError, ConnectionError) as e:
            print("Unable to retrieve metadata information.")
            print(e)
            raise

        self.labels = []
        for label in self.metadata_contents:
            self.labels.append(label)

    def list_datasets(self) -> List[str]:
        print(self.labels)
        return self.labels

    def dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        for i in self.metadata_contents[str(dataset_name).upper()]:
            print(f"{i}: {self.metadata_contents[str(dataset_name).upper()][i]} ")
            print("")
        return self.metadata_contents

    def insert_docs(
        self,
        collection: StandardCollection,
        docs: List[Dict[Any, Any]],
        collection_name: str,
    ) -> None:
        try:
            with progress(f"Collection: {collection_name}") as p:
                p.add_task("insert_docs")

                collection.import_bulk(docs)

        except DocumentInsertError as exec:
            print("Document insertion failed due to the following error:")
            print(exec.message)

        print(f"Finished loading current file for collection: {collection_name}")

    def load_file(self, collection_name: str, edge_type: bool, file_url: str) -> None:
        collection: StandardCollection

        try:
            collection = self.user_db.create_collection(collection_name, edge=edge_type)
        except CollectionCreateError as exec:
            print(
                f"""Failed to create {collection_name} collection due
                 to the following error:"""
            )
            print(exec.error_message)
            sys.exit(1)

        try:
            with progress(f"Downloading file for: {collection_name}") as p:
                p.add_task("load_file")
                data = requests.get(file_url).json()
        except (HTTPError, ConnectionError) as e:
            print("Unable to download file.")
            print(e)
            raise
        print(f"Downloaded file for: {collection_name}, now importing... ")
        self.insert_docs(collection, data, collection_name)

    def load(self, dataset_name: str) -> None:

        if str(dataset_name).upper() in self.labels:

            for edge in self.metadata_contents[str(dataset_name).upper()]["edges"]:
                for e in edge["files"]:
                    self.load_file(edge["collection_name"], True, e)

            for vertex in self.metadata_contents[str(dataset_name).upper()]["vertices"]:
                for v in vertex["files"]:
                    self.load_file(vertex["collection_name"], False, v)

        else:
            print(f"Dataset `{str(dataset_name.upper())}` not found")
            sys.exit(1)
