import sqlite3
import unicodedata

from sqlalchemy import event
from sqlalchemy.engine import Engine


def normalize_text(value):

    if not value:
        return ""

    value = unicodedata.normalize(
        "NFD",
        value,
    )

    value = "".join(
        char
        for char in value
        if unicodedata.category(char) != "Mn"
    )

    return value.lower()


def compare_ptbr(value_a, value_b):

    a = normalize_text(value_a)
    b = normalize_text(value_b)

    return (a > b) - (a < b)


@event.listens_for(Engine, "connect")
def register_sqlite_collation(
    dbapi_connection,
    connection_record,
):

    if isinstance(
        dbapi_connection,
        sqlite3.Connection,
    ):

        dbapi_connection.create_collation(
            "PTBR",
            compare_ptbr,
        )