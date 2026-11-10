"""Lambda (admin): list registrations by zip code."""
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('vaccTableM')


def getUserByZipcode(event, context):
    """List the registrations of a zip code area (uses the PLZ-index GSI).

    Trigger : POST /admin/getuserbyzipcode, protected by the Cognito authorizer
    Event   : {"PLZ": "<zip code>"}
    Returns : people with priority group <= 3, ordered by priority group (the GSI sort key)
    """
    plz = event["PLZ"]

    try:
        response = table.query(
            TableName='vaccTableM',
            IndexName='PLZ-index',
            Select='ALL_PROJECTED_ATTRIBUTES',
            KeyConditionExpression=Key('PLZ').eq(plz) & Key('Priorisierungsgruppe').lte(3))
        return response["Items"]
    except KeyError as e:
        "Something went wrong..."
