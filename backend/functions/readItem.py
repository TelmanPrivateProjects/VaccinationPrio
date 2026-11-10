"""Lambda: read a single registration from vaccTableM."""
import json
import boto3

client = boto3.resource('dynamodb')


def readItem(event, context):
    """Return the profile of the logged-in person.

    Trigger : POST /user/readitem, protected by the custom lambdaAuthorizer
    Event   : {"ID": <id>} - injected by the API Gateway request template from
              the authorizer context, so users can only ever read their own record
    Returns : the DynamoDB item, or an error message if no item exists
    """
    table = client.Table('vaccTableM')
    retTable = table.get_item(Key={'ID': event["ID"]})
    try:
        return retTable["Item"]
    except KeyError as e:
        return "No entry with id " + str(event["ID"]) + " found!"
