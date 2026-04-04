import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('vaccTableM')


def getUserByZipcode(event, context):
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
