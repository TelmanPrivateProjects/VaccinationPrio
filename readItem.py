import json
import boto3

client = boto3.resource('dynamodb')


def readItem(event, context):
    table = client.Table('vaccTableM')
    retTable = table.get_item(Key={'ID': event["ID"]})
    try:
        return retTable["Item"]
    except KeyError as e:
        return "No entry with id " + str(event["ID"]) + " found!"
