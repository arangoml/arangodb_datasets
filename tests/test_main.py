from typing import Any, no_type_check

import pytest
from requests import ConnectionError

from arango_datasets.datasets import Datasets

from .conftest import cleanup_collections, db

global test_metadata_url
global root_metadata_url
global bad_metadata_url
test_metadata_url = (
    "https://arangodb-dataset-library.s3.amazonaws.com/test_metadata.json"  # noqa: E501
)
root_metadata_url = (
    "https://arangodb-dataset-library.s3.amazonaws.com/root_metadata.json"  # noqa: E501
)
bad_metadata_url = "http://bad_url.arangodb.com/"


@no_type_check
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
        metadata_file=root_metadata_url,
    )
    with pytest.raises(TypeError):
        assert Datasets(
            db="some none db object",
            batch_size=1000,
            metadata_file=root_metadata_url,
        )
    with pytest.raises(Exception):
        assert Datasets({})

    with pytest.raises(ConnectionError):
        assert Datasets(db, metadata_file=bad_metadata_url)


@no_type_check
def test_list_datasets(capfd: Any) -> None:
    datasets = Datasets(
        db,
        metadata_file=test_metadata_url,
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
        metadata_file=test_metadata_url,
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
    file_url = "https://arangodb-dataset-library.s3.amazonaws.com/test_files/json/vertex_collection/test_vertex.json"  # noqa: E501
    collection = db.create_collection("test_vertex")
    assert None == (
        Datasets.load_json(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url=file_url,
            collection=collection,
        )
    )


@no_type_check
def json_bad_url() -> None:
    cleanup_collections()
    collection_name = "test_vertex"
    edge_type = False
    collection = db.create_collection("test_vertex")

    with pytest.raises(ConnectionError):
        Datasets.load_json(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url=bad_metadata_url,
            collection=collection,
        )


@no_type_check
def test_load_jsonl() -> None:
    cleanup_collections()
    collection_name = "test_vertex"
    edge_type = False
    file_url = "https://arangodb-dataset-library.s3.amazonaws.com/test_files/jsonl/vertex_collection/test_vertex.jsonl"  # noqa: E501
    collection = db.create_collection("test_vertex")
    assert None == (
        Datasets.load_jsonl(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url=file_url,
            collection=collection,
        )
    )


@no_type_check
def jsonl_bad_url() -> None:
    cleanup_collections()
    collection_name = "test_vertex"
    edge_type = False
    collection = db.create_collection("test_vertex")
    with pytest.raises(ConnectionError):
        Datasets.load_jsonl(
            Datasets(db),
            collection_name=collection_name,
            edge_type=edge_type,
            file_url=bad_metadata_url,
            collection=collection,
        )


@no_type_check
def test_load() -> None:
    cleanup_collections()
    Datasets(
        db,
        metadata_file=test_metadata_url,
    ).load("TEST")
    with pytest.raises(Exception):
        Datasets(db).load(2)
    assert db.collection("test_vertex").count() == 2
    assert db.collection("test_edge").count() == 1
