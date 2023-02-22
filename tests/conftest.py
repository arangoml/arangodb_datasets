from typing import Any

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import CollectionDeleteError

db: StandardDatabase


def pytest_addoption(parser: Any) -> None:
    parser.addoption("--url", action="store", default="http://localhost:8529")
    parser.addoption("--dbName", action="store", default="_system")
    parser.addoption("--username", action="store", default="root")
    parser.addoption("--password", action="store", default="openSesame")


def pytest_configure(config: Any) -> None:
    global db
    con = {
        "url": config.getoption("url"),
        "username": config.getoption("username"),
        "password": config.getoption("password"),
        "dbName": config.getoption("dbName"),
    }

    print("----------------------------------------")
    print("URL: " + con["url"])
    print("Username: " + con["username"])
    print("Password: " + con["password"])
    print("Database: " + con["dbName"])
    print("----------------------------------------")

    db = ArangoClient(hosts=con["url"]).db(
        con["dbName"], con["username"], con["password"], verify=True
    )
    cleanup_collections()


def cleanup_collections() -> None:
    global db
    if db.has_collection("test_vertex"):
        try:
            db.delete_collection("test_vertex")
        except CollectionDeleteError:
            print("unable to delete test_vertex")

    if db.has_collection("test_edge"):
        try:
            db.delete_collection("test_edge")
        except CollectionDeleteError:
            print("unable to delete test_edge")
