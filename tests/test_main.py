from typing import Any, no_type_check

import pytest
from requests import ConnectionError

from arango_datasets.datasets import Datasets

from .conftest import cleanup_collections, db


def test_dataset_constructor() -> None:
    assert Datasets(db)
    assert Datasets(db, batch_size=1000)
    assert Datasets(
        db,
        batch_size=1000,
    )
    assert Datasets(
        db,
        batch_size=1000,
        metadata_file="https://arangodb-dataset-library.s3.amazonaws.com/root_metadata.json",  # noqa: E501
    )
    with pytest.raises(Exception):
        assert Datasets({})  # type: ignore

    with pytest.raises(Exception):
        assert Datasets(db, metadata_file="bad_url")


def test_list_datasets(capfd: Any) -> None:
    datasets = Datasets(
        db,
        metadata_file="https://arangodb-dataset-library.s3.amazonaws.com/test_metadata.json",
    ).list_datasets()
    out, err = capfd.readouterr()
    assert "TEST" in out
    assert type(datasets) is list
    assert "TEST" in datasets


@no_type_check
def test_dataset_info(capfd: Any) -> None:
    with pytest.raises(Exception):
        Datasets.dataset_info()

    with pytest.raises(Exception):
        Datasets(db).dataset_info(2)

    dataset = Datasets(
        db,
        metadata_file="https://arangodb-dataset-library.s3.amazonaws.com/test_metadata.json",
    ).dataset_info("TEST")
    assert type(dataset) is dict

    assert dataset["TEST"]["file_type"] == "json"

    out, err = capfd.readouterr()
    assert len(out) > 0


@no_type_check
def test_load_file() -> None:
    with pytest.raises(Exception):
        Datasets.load_file(collection_name="test", edge_type=None, file_url="false")


@no_type_check
def test_load_json() -> None:
    cleanup_collections()
    collection_name = "test_vertex"
    edge_type = False
    file_url = """
    https://arangodb-dataset-library.s3.amazonaws.com/test_files/json/vertex_collection/test_vertex.json
    """
    collection = db.create_collection("test_vertex")
    assert (
        Datasets.load_json(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url=file_url,
            collection=collection,
        )
        == None
    )
    with pytest.raises(ConnectionError):
        Datasets.load_json(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url="http://bad_url.arangodb.com/",
            collection=collection,
        ) == None


@no_type_check
def test_load_jsonl() -> None:
    cleanup_collections()
    collection_name = "test_vertex"
    edge_type = False
    file_url = """
    https://arangodb-dataset-library.s3.amazonaws.com/test_files/jsonl/vertex_collection/test_vertex.jsonl
    """
    collection = db.create_collection("test_vertex")
    assert (
        Datasets.load_jsonl(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url=file_url,
            collection=collection,
        )
        == None
    )
    with pytest.raises(ConnectionError):
        Datasets.load_jsonl(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url="http://bad_url.arangodb.com/",
            collection=collection,
        ) == None


@no_type_check
def test_load() -> None:
    cleanup_collections()
    Datasets(
        db,
        metadata_file="https://arangodb-dataset-library.s3.amazonaws.com/test_metadata.json",
    ).load("TEST")
    with pytest.raises(Exception):
        Datasets(db).load(2)
    assert db.collection("test_vertex").count() == 2
    assert db.collection("test_edge").count() == 1
