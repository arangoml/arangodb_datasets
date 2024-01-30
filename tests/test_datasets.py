import pytest
from requests import ConnectionError

from arango_datasets.datasets import Datasets

from .conftest import cleanup_collections, db

test_metadata_url = "https://arangodb-dataset-library-ml.s3.amazonaws.com/test_metadata.json"  # noqa: E501
bad_metadata_url = "http://bad_url.arangodb.com/"


def test_dataset_constructor() -> None:
    with pytest.raises(Exception):
        Datasets({})

    with pytest.raises(TypeError):
        Datasets(db="some none db object")

    with pytest.raises(ConnectionError):
        Datasets(db, metadata_file=bad_metadata_url)


def test_list_datasets() -> None:
    datasets = Datasets(db, metadata_file=test_metadata_url).list_datasets()
    assert type(datasets) is list
    assert "TEST" in datasets


def test_dataset_info() -> None:
    with pytest.raises(ValueError):
        Datasets(db).dataset_info("invalid")

    datasets = Datasets(db, metadata_file=test_metadata_url)

    dataset = datasets.dataset_info("TEST")
    assert type(dataset) is dict
    assert dataset["file_type"] == "json"

    dataset = datasets.dataset_info("TEST_JSONL")
    assert type(dataset) is dict
    assert dataset["file_type"] == "jsonl"


def test_load_json() -> None:
    cleanup_collections()
    Datasets(db, metadata_file=test_metadata_url).load("TEST")
    assert db.collection("test_vertex").count() == 2
    assert db.collection("test_edge").count() == 1
    assert db.has_graph("TEST")


def test_load_jsonl() -> None:
    cleanup_collections()
    Datasets(db, metadata_file=test_metadata_url).load("TEST_JSONL")
    assert db.collection("test_vertex").count() == 2
    assert db.collection("test_edge").count() == 1
    assert db.has_graph("TEST_JSONL")
