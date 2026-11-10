"""Shared fixtures: an in-memory AWS (moto) with the same tables as serverless.yml."""
import importlib
import os
import sys
from datetime import date
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "functions"))

REGION = "eu-central-1"
os.environ.update({
    "AWS_DEFAULT_REGION": REGION,
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
})
os.environ.setdefault("SENDER_EMAIL", "noreply@example.com")
os.environ.setdefault("UPDATE_PRIO_FUNCTION", "DSG-Task3-M-test-updatePrio")

PLZ = "96047"


@pytest.fixture
def aws():
    """Start moto and create vaccTableM, datesTableM and a verified SES sender."""
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name=REGION)
        ddb.create_table(
            TableName="vaccTableM",
            AttributeDefinitions=[
                {"AttributeName": "ID", "AttributeType": "N"},
                {"AttributeName": "PLZ", "AttributeType": "S"},
                {"AttributeName": "Priorisierungsgruppe", "AttributeType": "N"},
            ],
            KeySchema=[{"AttributeName": "ID", "KeyType": "HASH"}],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "PLZ-index",
                    "KeySchema": [
                        {"AttributeName": "PLZ", "KeyType": "HASH"},
                        {"AttributeName": "Priorisierungsgruppe", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "Prio-index",
                    "KeySchema": [{"AttributeName": "Priorisierungsgruppe", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        ddb.create_table(
            TableName="datesTableM",
            AttributeDefinitions=[
                {"AttributeName": "PLZ", "AttributeType": "S"},
                {"AttributeName": "Datum", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PLZ", "KeyType": "HASH"},
                {"AttributeName": "Datum", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        boto3.client("ses", region_name=REGION).verify_domain_identity(
            Domain=os.environ["SENDER_EMAIL"].split("@")[1])
        yield ddb


@pytest.fixture
def load(aws):
    """Import a handler module inside the moto context (modules create boto3 clients at import)."""
    def _load(name):
        return importlib.reload(importlib.import_module(name))
    return _load


@pytest.fixture
def vacc(aws):
    return aws.Table("vaccTableM")


@pytest.fixture
def dates(aws):
    return aws.Table("datesTableM")


def add_person(table, id, prio, plz=PLZ, **extra):
    item = {"ID": id, "PLZ": plz, "Priorisierungsgruppe": prio,
            "Mail": f"person{id}@example.com", "Geburtstag": "01-01-1980", **extra}
    table.put_item(Item=item)
    return item


def appointment(table, id):
    return table.get_item(Key={"ID": id})["Item"].get("Termin")


def emails_sent():
    return int(boto3.client("ses", region_name=REGION).get_send_quota()["SentLast24Hours"])


def birthday_for_age(age):
    """Return a "dd-mm-yyyy" birthday for someone who is exactly `age` years old today."""
    today = date.today()
    day = 28 if (today.month, today.day) == (2, 29) else today.day
    return f"{day:02d}-{today.month:02d}-{today.year - age}"
