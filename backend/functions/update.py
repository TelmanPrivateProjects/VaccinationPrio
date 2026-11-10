"""Lambdas: profile updates, priority recalculation and legacy data migration."""
import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from datetime import date

dynamodb = boto3.resource('dynamodb')
client = boto3.client('lambda')
table = dynamodb.Table('vaccTableM')
# Name of the deployed updatePrio function (<service>-<stage>-updatePrio), set in serverless.yml.
# Every profile update invokes it, so the priority group is always derived from the latest data.
fnameUpdatePrio = os.environ.get('UPDATE_PRIO_FUNCTION', 'DSG-Task3-M-dev-updatePrio')


# ---------------------------------------------------------------------------
# Profile update handlers
#
# Trigger : POST /user/update<field>?<param>=<value>, protected by the custom
#           lambdaAuthorizer. The API Gateway request template builds the event
#           from the authorizer context (ID) and the query string parameter, so
#           a user can only change their own record.
# Flow    : 1. update the field in vaccTableM
#           2. emit a follow-up event by invoking updatePrio for this ID
#              (synchronous Lambda-to-Lambda call) to recompute the priority group
# ---------------------------------------------------------------------------


def updateLastName(event, context):
    """Update the last name (event: ID, name)."""
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
    """Update the first name (event: ID, vorname)."""
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
    """Update the e-mail address (event: ID, mail)."""
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
    """Update the birthday (event: ID, geburtstag "dd-mm-yyyy"); changes the age-based group."""
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
    """Update the zip code (event: ID, plz)."""
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
    """Update the gender (event: ID, geschlecht = m | w | d)."""
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
    """Update the critical-infrastructure flag (event: ID, systemrelevanz)."""
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
    """Update the pre-existing-conditions flag (event: ID, healthPr)."""
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


# ---------------------------------------------------------------------------
# Internal event handlers
# ---------------------------------------------------------------------------

def updatePrio(event, context):
    """Recompute and store the priority group of one person.

    Trigger : invoked by the profile update handlers and by updateOldData
              (no HTTP endpoint)
    Event   : {"ID": <id>}
    Rules   : same as in writeItem - 1 = age >= 60, 2 = age 40-59, 3 = age 18-39,
              -1 = under 18; group 3 moves up to 2 with systemrelevanz or vorerkrankungen
    """
    id = event["ID"]

    entry = table.query(KeyConditionExpression=Key('ID').eq(id))

    # Older records may not have the risk-factor attributes yet; treat them as False
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
    """Migrate up to `n` legacy records of a zip code area to the current data model.

    Trigger : POST /admin/updateolddata, protected by the Cognito authorizer
    Event   : {"plz": "<zip code>", "n": <max records>}
    Flow    : selects records without a `Version` attribute, recomputes their
              priority (invokes updatePrio) and sets Systemrelevanz/Vorerkrankungen
              to False and Version to 1
    """

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
