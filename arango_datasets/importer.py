import requests
from requests import HTTPError, ConnectionError
from typing import Optional
from arango.database import Database
from arango.exceptions import CollectionCreateError, DocumentInsertError
from arango.collection import StandardCollection

from .utils import progress


class Importer:
    def __init__(
        self,
        db: Database,
        batch_size: Optional[int] = None,
        dataset_repository: str = "https://arangodb-dataset-library.s3.amazonaws.com",
        metadata_file: str =
        "https://arangodb-dataset-library.s3.amazonaws.com/root_metadata.json",
    ):
        self.metadata_file: str = metadata_file
        self.metadata_contents: dict
        self.batch_size = batch_size
        self.url = dataset_repository
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

    # TODO
    def list_datasets(self):
        print(self.labels)

    def dataset_info(self, dataset_name: str):
        for i in self.metadata_contents[str(dataset_name).upper()]:
            print(f"{i}: {self.metadata_contents[str(dataset_name).upper()][i]} ")
            print("")

    def insert_docs(
        self, collection: StandardCollection, docs: list, collection_name: str
    ):
        try:
            with progress(f"Collection: {collection_name}") as p:
                p.add_task("insert_docs")

                collection.import_bulk(docs)

        except DocumentInsertError as exec:
            print("Document insertion failed due to the following error:")
            print(exec.message)

        print(f"Finished loading current file for collection: {collection_name}")

    def load_file(self, collection_name: str, edge_type: bool, file_url: str):
        collection: StandardCollection

        try:
            collection = self.user_db.create_collection(collection_name, edge=edge_type)
        except CollectionCreateError as exec:
            print(f"Failed to create {collection_name} due to the following error:")
            print(exec.message)
            raise

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

    def load(self, dataset_name: str):

        if str(dataset_name).upper() in self.labels:

            for edge in self.metadata_contents[str(dataset_name).upper()]["edges"]:
                for e in edge["files"]:
                    self.load_file(edge["collection_name"], True, e)

            for vertex in self.metadata_contents[str(dataset_name).upper()]["vertices"]:
                for v in vertex["files"]:
                    self.load_file(vertex["collection_name"], False, v)

        else:
            print(f"Dataset `{str(dataset_name.upper())}` not found")
            return
