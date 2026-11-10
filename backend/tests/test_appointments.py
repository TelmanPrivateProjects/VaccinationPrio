"""Appointment allocation: addFreeDates and distributeDates."""
from conftest import PLZ, add_person, appointment, emails_sent

DAY = "2021-12-24"


# --- addFreeDates --------------------------------------------------------------

def test_add_free_dates_assigns_every_slot(load, vacc, dates):
    addFreeDates = load("addFreeDates")
    for id, prio in [(1, 1), (2, 2), (3, 3), (4, 3)]:
        add_person(vacc, id, prio)

    addFreeDates.addFreeDates({"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00", "09:15", "09:30", "09:45"]}, None)

    assert all(appointment(vacc, id) for id in [1, 2, 3, 4])
    assert sorted(appointment(vacc, id) for id in [1, 2, 3, 4]) == [
        f"{DAY}-09:00", f"{DAY}-09:15", f"{DAY}-09:30", f"{DAY}-09:45"]
    assert dates.scan()["Items"] == []          # no slot left over
    assert emails_sent() == 4


def test_add_free_dates_serves_highest_priority_first(load, vacc, dates):
    addFreeDates = load("addFreeDates")
    add_person(vacc, 1, 3)
    add_person(vacc, 2, 1)
    add_person(vacc, 3, 2)

    addFreeDates.addFreeDates({"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00"]}, None)

    assert appointment(vacc, 2) == f"{DAY}-09:00"
    assert appointment(vacc, 1) is None and appointment(vacc, 3) is None


def test_add_free_dates_never_books_minors(load, vacc, dates):
    addFreeDates = load("addFreeDates")
    add_person(vacc, 1, -1)   # under 18
    add_person(vacc, 2, 3)

    addFreeDates.addFreeDates({"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00", "09:15"]}, None)

    assert appointment(vacc, 1) is None
    assert appointment(vacc, 2) == f"{DAY}-09:00"
    assert dates.get_item(Key={"PLZ": PLZ, "Datum": DAY})["Item"]["Termine"] == ["09:15"]


def test_add_free_dates_appends_leftovers_to_existing_day(load, vacc, dates):
    addFreeDates = load("addFreeDates")
    dates.put_item(Item={"PLZ": PLZ, "Datum": DAY, "Termine": ["08:00"]})

    addFreeDates.addFreeDates({"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00", "09:15"]}, None)

    assert dates.get_item(Key={"PLZ": PLZ, "Datum": DAY})["Item"]["Termine"] == ["08:00", "09:00", "09:15"]


# --- distributeDates -----------------------------------------------------------

def test_distribute_more_slots_than_people_keeps_the_rest(load, vacc, dates):
    distributeDates = load("distributeDates")
    add_person(vacc, 1, 1)
    add_person(vacc, 2, 2)
    dates.put_item(Item={"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00", "09:15", "09:30"]})

    distributeDates.distributeDates({"PLZ": PLZ, "n": 2}, None)

    assert appointment(vacc, 1) == f"{DAY}-09:00"
    assert appointment(vacc, 2) == f"{DAY}-09:15"
    assert dates.get_item(Key={"PLZ": PLZ, "Datum": DAY})["Item"]["Termine"] == ["09:30"]
    assert emails_sent() == 2


def test_distribute_across_several_days(load, vacc, dates):
    distributeDates = load("distributeDates")
    for id in [1, 2, 3]:
        add_person(vacc, id, 2)
    dates.put_item(Item={"PLZ": PLZ, "Datum": "2021-12-23", "Termine": ["10:00"]})
    dates.put_item(Item={"PLZ": PLZ, "Datum": "2021-12-24", "Termine": ["09:00", "09:15"]})

    distributeDates.distributeDates({"PLZ": PLZ, "n": 3}, None)

    assert all(appointment(vacc, id) for id in [1, 2, 3])
    assert dates.scan()["Items"] == []          # both days fully used and deleted


def test_distribute_is_capped_by_waiting_people(load, vacc, dates):
    distributeDates = load("distributeDates")
    add_person(vacc, 1, 1)
    dates.put_item(Item={"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00", "09:15"]})

    distributeDates.distributeDates({"PLZ": PLZ, "n": 5}, None)

    assert appointment(vacc, 1) == f"{DAY}-09:00"
    assert dates.get_item(Key={"PLZ": PLZ, "Datum": DAY})["Item"]["Termine"] == ["09:15"]


def test_distribute_never_books_minors(load, vacc, dates):
    distributeDates = load("distributeDates")
    add_person(vacc, 1, -1)
    add_person(vacc, 2, 3)
    dates.put_item(Item={"PLZ": PLZ, "Datum": DAY, "Termine": ["09:00", "09:15"]})

    distributeDates.distributeDates({"PLZ": PLZ, "n": 2}, None)

    assert appointment(vacc, 1) is None
    assert appointment(vacc, 2) == f"{DAY}-09:00"
