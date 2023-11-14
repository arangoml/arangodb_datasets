import json
import sys
from typing import Any, Dict, List

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
    :param preserve_existing: Boolean to preserve existing data and graph definiton
    type preserve_existing: bool
    """

    def __init__(
        self,
        db: Database,
        batch_size: int = 50,
        metadata_file: str = "https://arangodb-dataset-library-ml.s3.amazonaws.com/root_metadata.json",  # noqa: E501
        preserve_existing: bool = False,
    ):
        self.metadata_file: str = metadata_file
        self.metadata_contents: Dict[str, Any]
        self.batch_size = batch_size
        self.user_db = db
        self.preserve_existing = preserve_existing
        self.file_type: str
        if issubclass(type(db), Database) is False:
            msg = "**db** parameter must inherit from arango.database.Database"
            raise TypeError(msg)

        try:
            response = requests.get(self.metadata_file, timeout=6000)
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

                collection.import_bulk(docs, batch_size=self.batch_size)

        except DocumentInsertError as exec:
            print("Document insertion failed due to the following error:")
            print(exec.message)
            sys.exit(1)

        print(f"Finished loading current file for collection: {collection_name}")

    def load_json(
        self,
        collection_name: str,
        edge_type: bool,
        file_url: str,
        collection: StandardCollection,
    ) -> None:
        try:
            with progress(f"Downloading file for: {collection_name}") as p:
                p.add_task("load_file")
                data = requests.get(file_url, timeout=6000).json()
        except (HTTPError, ConnectionError) as e:
            print("Unable to download file.")
            print(e)
            raise e
        print(f"Downloaded file for: {collection_name}, now importing... ")
        self.insert_docs(collection, data, collection_name)

    def load_jsonl(
        self,
        collection_name: str,
        edge_type: bool,
        file_url: str,
        collection: StandardCollection,
    ) -> None:
        json_data = []
        try:
            with progress(f"Downloading file for: {collection_name}") as p:
                p.add_task("load_file")
                data = requests.get(file_url, timeout=6000)

            if data.encoding is None:
                data.encoding = "utf-8"

            for line in data.iter_lines(decode_unicode=True):
                if line:
                    json_data.append(json.loads(line))

        except (HTTPError, ConnectionError) as e:
            print("Unable to download file.")
            print(e)
            raise
        print(f"Downloaded file for: {collection_name}, now importing... ")
        self.insert_docs(collection, json_data, collection_name)

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
        if self.file_type == "json":
            self.load_json(collection_name, edge_type, file_url, collection)
        elif self.file_type == "jsonl":
            self.load_jsonl(collection_name, edge_type, file_url, collection)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    def cleanup_collections(self, collection_name: str) -> None:
        if (
            self.user_db.has_collection(collection_name)
            and self.preserve_existing is False
        ):
            print(
                f"""
                Old collection found
                ${collection_name},
                dropping and creating with new data."""
            )
            self.user_db.delete_collection(collection_name)

    def load(self, dataset_name: str) -> None:
        if str(dataset_name).upper() in self.labels:
            self.file_type = self.metadata_contents[str(dataset_name).upper()][
                "file_type"
            ]

            for edge in self.metadata_contents[str(dataset_name).upper()]["edges"]:
                self.cleanup_collections(collection_name=edge["collection_name"])
                for e in edge["files"]:
                    self.load_file(edge["collection_name"], True, e)

            for vertex in self.metadata_contents[str(dataset_name).upper()]["vertices"]:
                self.cleanup_collections(collection_name=vertex["collection_name"])
                for v in vertex["files"]:
                    self.load_file(vertex["collection_name"], False, v)

        else:
            print(f"Dataset `{str(dataset_name.upper())}` not found")
            sys.exit(1)
