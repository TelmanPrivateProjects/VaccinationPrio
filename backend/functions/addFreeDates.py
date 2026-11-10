"""Lambda (admin): add vaccination slots, assign them and notify people by e-mail."""
import boto3
import botocore
from boto3.dynamodb.conditions import Key


def addFreeDates(event, context):
    """Publish new vaccination slots for a zip code area and day.

    Trigger : POST /admin/addfreedates, protected by the Cognito authorizer
    Event   : {"PLZ": "<zip code>", "Datum": "<day>", "Termine": ["<time>", ...]}
    Flow    : 1. assign the new slots directly to people in that zip code
                 who have no appointment yet (highest priority first) and notify
                 each of them by e-mail (SES)
              2. store the remaining, unassigned slots in datesTableM so they can
                 be handed out later by distributeDates
    """

    dynamodb = boto3.resource('dynamodb')
    datesTableM = dynamodb.Table('datesTableM')
    vaccTableM = dynamodb.Table('vaccTableM')
    ses = boto3.client('ses')

    try:

        plz = event["PLZ"]
        datum = event["Datum"]
        termine = event["Termine"]
        i = 0

        # People in this zip code with priority group <= 3 and no appointment yet,
        # returned in priority order by the PLZ-index sort key
        response = vaccTableM.query(
            TableName='vaccTableM',
            IndexName='PLZ-index',
            Select='ALL_PROJECTED_ATTRIBUTES',
            KeyConditionExpression=Key('PLZ').eq(
                plz) & Key('Priorisierungsgruppe').lte(3),
            FilterExpression="attribute_not_exists(Termin)")

        entries = response["Items"]

        if entries:
            for termin in event["Termine"]:
                if len(entries) > i:
                    vaccTableM.update_item(
                        Key={
                            'ID': entries[i]["ID"]
                        },
                        UpdateExpression="SET Termin = :t",
                        ExpressionAttributeValues={
                            ':t': datum+"-"+termin
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    # Notify the person; a failed e-mail does not undo the booking
                    try:
                        ses.send_email(
                            Source='maximilian.goetz@stud.uni-bamberg.de',
                            Destination={
                                'ToAddresses': [
                                    entries[i]["Mail"]
                                ]
                            },
                            Message={
                                'Subject': {
                                    'Data': 'Impftermin',
                                    'Charset': 'utf-8'
                                },
                                'Body': {
                                    'Text': {
                                        'Data': "Ihr Impftermin ist am "+datum+", um "+termin+" Uhr.",
                                        'Charset': 'utf-8'
                                    }
                                }
                            }
                        )
                    except botocore.exceptions.ClientError as e:
                        print("No email send")

                    termine.remove(termin)
                    i = i+1
                else:
                    break

        # Keep the slots that were not assigned as free dates (append to existing ones)
        existingDates = datesTableM.query(
            TableName='datesTableM',
            KeyConditionExpression=Key('PLZ').eq(plz) & Key('Datum').eq(datum))
        existingDatesEntrie = existingDates["Items"]

        if existingDatesEntrie:
            if termine:
                dates = existingDatesEntrie[0]["Termine"] + termine
                datesTableM.update_item(
                    Key={
                        'PLZ': plz,
                        'Datum': datum,
                    },
                    UpdateExpression="SET Termine = :t",
                    ExpressionAttributeValues={
                        ':t': dates
                    },
                    ReturnValues="UPDATED_NEW"
                )
        else:
            if termine:
                datesTableM.update_item(
                    Key={
                        'PLZ': plz,
                        'Datum': datum,
                    },
                    UpdateExpression="SET Termine = :t",
                    ExpressionAttributeValues={
                        ':t': termine
                    },
                    ReturnValues="UPDATED_NEW"
                )

        return "Entry added!"
    except KeyError as e:
        return "Something went wrong ..."
