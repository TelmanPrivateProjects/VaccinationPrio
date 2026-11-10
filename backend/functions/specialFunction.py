"""Lambda (admin): pick the oldest people of a priority group in a zip code area."""
import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

client = boto3.resource('dynamodb')


def specialFunction(event, context):
    """Return the `amount` oldest people of a priority group in a zip code area.

    Trigger : POST /admin/specialfunction, protected by the Cognito authorizer
    Event   : {"PLZ": "<zip code>", "prio": <group>, "amount": <n>}
    Returns : list of people sorted by birthday (oldest first), at most `amount`
    """

    table = client.Table('vaccTableM')
    plz = event["PLZ"]
    amount = event["amount"]
    prio = event["prio"]

    try:
        scanResponse = table.scan(FilterExpression=Attr("PLZ").eq(
            plz) & Attr("Priorisierungsgruppe").eq(prio))
        items = scanResponse["Items"]
        # Oldest first: sort by birthday ascending
        ListSorted = sorted(items, key=lambda d: datetime.strptime(
            d['Geburtstag'], '%d-%m-%Y'))
        return ListSorted[:amount]

    except KeyError as e:
        return "An error occured"
