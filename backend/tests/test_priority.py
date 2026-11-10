"""Priority rules on registration (writeItem) and recalculation after updates (updatePrio)."""
import json

import pytest

from conftest import add_person, birthday_for_age

REGISTRATION = {
    "name": "Muster", "vorname": "Max", "mail": "max@example.com", "plz": "96047",
    "geschlecht": "m", "secret": "hash",
}


@pytest.mark.parametrize("age, sysrel, health, expected", [
    (75, False, False, 1),
    (60, False, False, 1),
    (59, False, False, 2),
    (40, False, False, 2),
    (39, False, False, 3),
    (18, False, False, 3),
    (30, True, False, 2),    # critical-infrastructure job moves group 3 up to 2
    (30, False, True, 2),    # pre-existing conditions move group 3 up to 2
    (65, True, True, 1),     # risk factors never lower a higher group
    (17, False, False, -1),  # under 18: not eligible
    (17, True, True, -1),
])
def test_write_item_assigns_priority_group(load, vacc, age, sysrel, health, expected):
    writeItem = load("writeItem")
    event = {**REGISTRATION, "geburtstag": birthday_for_age(age),
             "systemrelevanz": sysrel, "vorerkrankungen": health}

    assert writeItem.writeItem(event, None) == "Entry added!"

    [item] = vacc.scan()["Items"]
    assert item["Priorisierungsgruppe"] == expected


class FakeLambdaClient:
    """Stands in for boto3's Lambda client: runs updatePrio in-process."""

    def __init__(self, update_module):
        self.update = update_module
        self.invoked = []

    def get_function(self, FunctionName):
        return {"Configuration": {"FunctionArn": FunctionName}}

    def invoke(self, FunctionName, InvocationType, Payload):
        self.invoked.append(FunctionName)
        return self.update.updatePrio(json.loads(Payload), None)


def test_profile_update_emits_update_prio_event(load, vacc, monkeypatch):
    update = load("update")
    fake = FakeLambdaClient(update)
    monkeypatch.setattr(update, "client", fake)
    add_person(vacc, 1, 3, Geburtstag=birthday_for_age(30), Systemrelevanz=False, Vorerkrankungen=False)

    update.updateBirthday({"ID": 1, "geburtstag": birthday_for_age(70)}, None)

    assert fake.invoked == ["DSG-Task3-M-test-updatePrio"]  # function name comes from the environment
    assert vacc.get_item(Key={"ID": 1})["Item"]["Priorisierungsgruppe"] == 1


def test_update_prio_treats_missing_risk_flags_as_false(load, vacc):
    update = load("update")
    add_person(vacc, 1, 2, Geburtstag=birthday_for_age(25))  # legacy record without flags

    update.updatePrio({"ID": 1}, None)

    assert vacc.get_item(Key={"ID": 1})["Item"]["Priorisierungsgruppe"] == 3
