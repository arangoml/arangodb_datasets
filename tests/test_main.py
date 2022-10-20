from typing import Any, no_type_check

import pytest

from arango_datasets.datasets import Datasets

from .conftest import db


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
        assert Datasets({})

    with pytest.raises(Exception):
        assert Datasets(db, metadata_file="bad_url")


def test_list_datasets(capfd: Any) -> None:
    datasets = Datasets(db).list_datasets()
    out, err = capfd.readouterr()
    assert "FLIGHTS" in out
    assert type(datasets) is list
    assert "FLIGHTS" in datasets


@no_type_check
def test_dataset_info(capfd: Any) -> None:
    with pytest.raises(Exception):
        Datasets.dataset_info()

    with pytest.raises(Exception):
        Datasets(db).dataset_info(2)

    dataset = Datasets(db).dataset_info("FLIGHTS")
    assert type(dataset) is dict

    out, err = capfd.readouterr()
    assert len(out) > 0


@no_type_check
def test_load() -> None:
    Datasets(db).load("FLIGHTS")
    with pytest.raises(Exception):
        Datasets(db).load(2)
    assert db.collection("airports").count() == 3375
    assert db.collection("flights").count() == 286463
