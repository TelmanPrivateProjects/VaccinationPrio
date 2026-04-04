import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

client = boto3.resource('dynamodb')


def specialFunction(event, context):

    table = client.Table('vaccTableM')
    plz = event["PLZ"]
    amount = event["amount"]
    prio = event["prio"]

    try:
        scanResponse = table.scan(FilterExpression=Attr("PLZ").eq(
            plz) & Attr("Priorisierungsgruppe").eq(prio))
        items = scanResponse["Items"]
        ListSorted = sorted(items, key=lambda d: datetime.strptime(
            d['Geburtstag'], '%d-%m-%Y'))
        return ListSorted[:amount]

    except KeyError as e:
        return "An error occured"
