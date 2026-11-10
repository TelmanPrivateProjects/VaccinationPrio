"""Lambda: delete a registration from vaccTableM."""
import json
import boto3

client = boto3.resource('dynamodb')


def deleteItem(event, context):
    """Delete a registration by ID.

    Trigger : direct invocation only (no HTTP endpoint is configured)
    Event   : {"ID": <id>}
    """
    table = client.Table('vaccTableM')

    try:
        table.delete_item(Key={'ID': event["ID"]})
        return "Entry successfully deleted!"
    except KeyError as e:
        return "No entry with id " + event["ID"] + " found!"
