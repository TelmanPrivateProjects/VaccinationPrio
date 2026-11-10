"""Lambda (admin): list registrations by priority group."""
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('vaccTableM')


def getUserByPrio(event, context):
    """List all registrations in one priority group (uses the Prio-index GSI).

    Trigger : POST /admin/getuserbyprio, protected by the Cognito authorizer
    Event   : {"prio": <group>}
    """
    prio = event["prio"]

    try:
        response = table.query(
            TableName='vaccTableM',
            IndexName='Prio-index',
            Select='ALL_PROJECTED_ATTRIBUTES',
            KeyConditionExpression=Key('Priorisierungsgruppe').eq(prio))
        return response["Items"]
    except KeyError as e:
        return "Something went wrong..."
