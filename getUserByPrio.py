import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('vaccTableM')


def getUserByPrio(event, context):
    prio = event["prio"]

    try:
        response = table.query(
            TableName='vaccTableM',
            IndexName='Prio-index',
            Select='ALL_PROJECTED_ATTRIBUTES',
            KeyConditionExpression=Key('Priorisierungsgruppe').eq(prio))
        return response["Items"]
    except KeyError as e:
        "Something went wrong..."
