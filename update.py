import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import date

dynamodb = boto3.resource('dynamodb')
client = boto3.client('lambda')
table = dynamodb.Table('vaccTableM')
fnameUpdatePrio = 'DSG-Task3-M-dev-updatePrio'


def updateLastName(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET #n= :n",
            ExpressionAttributeValues={
                ':n': event["name"]
            },
            ExpressionAttributeNames={
                "#n": "Name"
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateFirstName(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET Vorname= :v",
            ExpressionAttributeValues={
                ':v': event["vorname"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateMail(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET Mail= :m",
            ExpressionAttributeValues={
                ':m': event["mail"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateBirthday(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET Geburtstag= :g",
            ExpressionAttributeValues={
                ':g': event["geburtstag"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateZipcode(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET PLZ= :plz",
            ExpressionAttributeValues={
                ':plz': event["plz"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateGender(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET Geschlecht= :ge",
            ExpressionAttributeValues={
                ':ge': event["geschlecht"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateSysRel(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET Systemrelevanz= :s",
            ExpressionAttributeValues={
                ':s': event["systemrelevanz"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updateHealthPr(event, context):
    try:
        response = table.update_item(
            Key={
                'ID': event["ID"]
            },
            UpdateExpression="SET Vorerkrankungen= :h",
            ExpressionAttributeValues={
                ':h': event["healthPr"]
            },
            ReturnValues="UPDATED_NEW"
        )
        inputParams = {
            'ID': event['ID']
        }
        client.invoke(
            FunctionName=client.get_function(
                FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
            InvocationType='RequestResponse',
            Payload=json.dumps(inputParams)
        )
        return response
    except KeyError as e:
        return "Problem beim Aktualisieren!"


def updatePrio(event, context):
    id = event["ID"]

    entry = table.query(KeyConditionExpression=Key('ID').eq(id))

    try:
        sysrel = entry["Items"][0]["Systemrelevanz"]
    except KeyError as e:
        sysrel = False

    try:
        healthPr = entry["Items"][0]["Vorerkrankungen"]
    except KeyError as e:
        healthPr = False

    splitDate = entry["Items"][0]["Geburtstag"].split("-")
    birthDate = date(int(splitDate[2]), int(splitDate[1]), int(splitDate[0]))

    today = date.today()
    age = today.year - birthDate.year - \
        ((today.month, today.day) < (birthDate.month, birthDate.day))

    if age >= 60:
        prio = 1
    elif age < 60 and age >= 40:
        prio = 2
    elif age < 18:
        prio = -1
    else:
        prio = 3

    if prio == 3 and (sysrel or healthPr):
        prio = 2

    try:
        response = table.update_item(
            Key={
                'ID': id
            },
            UpdateExpression="set Priorisierungsgruppe = :p",
            ExpressionAttributeValues={
                ':p': prio
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except KeyError as e:
        return e


def updateOldData(event, context):

    plz = event["plz"]
    n = event["n"]

    response = table.query(
        TableName='vaccTableM',
        IndexName='PLZ-index',
        Select='ALL_PROJECTED_ATTRIBUTES',
        KeyConditionExpression=Key('PLZ').eq(
            plz) & Key('Priorisierungsgruppe').lte(3),
        FilterExpression="attribute_not_exists(Version)")

    entrys = response["Items"][:n]

    try:
        for entry in entrys:
            id = int(entry['ID'])
            inputParams = {
                'ID': id
            }
            client.invoke(
                FunctionName=client.get_function(
                    FunctionName=fnameUpdatePrio)['Configuration']['FunctionArn'],
                InvocationType='RequestResponse',
                Payload=json.dumps(inputParams)
            )
            table.update_item(
                Key={
                    'ID': entry['ID']
                },
                UpdateExpression="SET Systemrelevanz= :s, Vorerkrankungen= :vo, Version= :ve",
                ExpressionAttributeValues={
                    ':s': False,
                    ':vo': False,
                    ':ve': 1
                },
                ReturnValues="UPDATED_NEW"
            )
        return "Sucess"
    except KeyError as e:
        return "Something went wrong ..."
