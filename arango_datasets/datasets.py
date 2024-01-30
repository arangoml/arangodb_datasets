import json
from typing import Any, Callable, Dict, List, Optional

import requests
from arango.collection import StandardCollection
from arango.database import Database

from .utils import progress


class Datasets:
    """ArangoDB Example Datasets

    :param db: A python-arango database instance
    :type db: arango.database.Database
    :param batch_size: Optional batch size supplied to the
        python-arango `import_bulk` function. Defaults to 50.
    :type batch_size: int
    :param metadata_file: URL for datasets metadata file. Defaults to
        "https://arangodb-dataset-library-ml.s3.amazonaws.com/root_metadata.json".
    :type metadata_file: str
    :param preserve_existing: Whether to preserve the existing collections and
        graph of the dataset (if any). Defaults to False.
    type preserve_existing: bool
    """

    def __init__(
        self,
        db: Database,
        batch_size: int = 1000,
        metadata_file: str = "https://arangodb-dataset-library-ml.s3.amazonaws.com/root_metadata.json",  # noqa: E501
        preserve_existing: bool = False,
    ):
        if not isinstance(db, Database):
            msg = "**db** parameter must inherit from arango.database.Database"
            raise TypeError(msg)

        self.user_db = db
        self.batch_size = batch_size
        self.metadata_file = metadata_file
        self.preserve_existing = preserve_existing

        self.__metadata: Dict[str, Dict[str, Any]]
        self.__metadata = self.__get_response(self.metadata_file).json()
        self.__dataset_names = [n for n in self.__metadata]

    def list_datasets(self) -> List[str]:
        """List available datasets

        :return: Names of the available datasets to load.
        :rtype: List[str]
        """
        return self.__dataset_names

    def dataset_info(self, dataset_name: str) -> Dict[str, Any]:
        """Get information about a dataset

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :return: Some metadata about the dataset.
        :rtype: Dict[str, Any]
        :raises ValueError: If the dataset is not found.
        """
        if dataset_name.upper() not in self.__dataset_names:
            raise ValueError(f"Dataset '{dataset_name}' not found")

        info: Dict[str, Any] = self.__metadata[dataset_name.upper()]
        return info

    def load(
        self,
        dataset_name: str,
        batch_size: Optional[int] = None,
        preserve_existing: Optional[bool] = None,
    ) -> None:
        """Load a dataset into the database.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :param batch_size: Batch size supplied to the
            python-arango `import_bulk` function. Overrides the **batch_size**
            supplied to the constructor. Defaults to None.
        :type batch_size: Optional[int]
        :param preserve_existing: Whether to preserve the existing collections and
            graph of the dataset (if any). Overrides the **preserve_existing**
            supplied to the constructor. Defaults to False.
        :type preserve_existing: bool
        :raises ValueError: If the dataset is not found.
        """
        if dataset_name.upper() not in self.__dataset_names:
            raise ValueError(f"Dataset '{dataset_name}' not found")

        dataset_contents = self.__metadata[dataset_name.upper()]

        # Backwards compatibility
        self.batch_size = batch_size if batch_size is not None else self.batch_size
        self.preserve_existing = (
            preserve_existing
            if preserve_existing is not None
            else self.preserve_existing
        )

        file_type = dataset_contents["file_type"]
        load_file_function: Callable[[str], List[Dict[str, Any]]]
        if file_type == "json":
            load_file_function = self.__load_json
        elif file_type == "jsonl":
            load_file_function = self.__load_jsonl
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        for data, is_edge in [
            (dataset_contents["vertices"], False),
            (dataset_contents["edges"], True),
        ]:
            for col_data in data:
                col = self.__initialize_collection(col_data["collection_name"], is_edge)

                for file in col_data["files"]:
                    self.__import_bulk(col, load_file_function(file))

        if edge_definitions := dataset_contents.get("edge_definitions"):
            self.user_db.delete_graph(dataset_name, ignore_missing=True)
            self.user_db.create_graph(dataset_name, edge_definitions)

    def __get_response(self, url: str, timeout: int = 60) -> requests.Response:
        """Wrapper around requests.get() with a progress bar.

        :param url: URL to get a response from.
        :type url: str
        :param timeout: Timeout in seconds. Defaults to 60.
        :type timeout: int
        :raises ConnectionError: If the connection fails.
        :raises HTTPError: If the HTTP request fails.
        :return: The response from the URL.
        :rtype: requests.Response
        """
        with progress(f"GET: {url}") as p:
            p.add_task("get_response")

            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response

    def __initialize_collection(
        self, collection_name: str, is_edge: bool
    ) -> StandardCollection:
        """Initialize a collection.

        :param collection_name: Name of the collection.
        :type collection_name: str
        :param is_edge: Whether the collection is an edge collection.
        :type is_edge: bool
        :raises CollectionCreateError: If the collection cannot be created.
        :return: The collection.
        :rtype: arango.collection.StandardCollection
        """
        print(f"Initializing collection '{collection_name}'")

        if not self.preserve_existing:
            self.user_db.delete_collection(collection_name, ignore_missing=True)

        return self.user_db.create_collection(collection_name, edge=is_edge)

    def __load_json(self, file_url: str) -> List[Dict[str, Any]]:
        """Load a JSON file into memory.

        :param file_url: URL of the JSON file.
        :type file_url: str
        :raises ConnectionError: If the connection fails.
        :raises HTTPError: If the HTTP request fails.
        :return: The JSON data.
        :rtype: Dict[str, Any]
        """
        json_data: List[Dict[str, Any]] = self.__get_response(file_url).json()
        return json_data

    def __load_jsonl(self, file_url: str) -> List[Dict[str, Any]]:
        """Load a JSONL file into memory.

        :param file_url: URL of the JSONL file.
        :type file_url: str
        :raises ConnectionError: If the connection fails.
        :raises HTTPError: If the HTTP request fails.
        :return: The JSONL data as a list of dictionaries.
        """
        json_data = []
        data = self.__get_response(file_url)

        if data.encoding is None:
            data.encoding = "utf-8"

        for line in data.iter_lines(decode_unicode=True):
            if line:
                json_data.append(json.loads(line))

        return json_data

    def __import_bulk(
        self, collection: StandardCollection, docs: List[Dict[str, Any]]
    ) -> None:
        """Wrapper around python-arango's import_bulk() with a progress bar.

        :param collection: The collection to insert the documents into.
        :type collection: arango.collection.StandardCollection
        :param docs: The documents to insert.
        :type docs: List[Dict[Any, Any]]
        :raises DocumentInsertError: If the document cannot be inserted.
        """
        with progress(f"Collection: {collection.name}") as p:
            p.add_task("insert_docs")

            collection.import_bulk(docs, batch_size=self.batch_size)
