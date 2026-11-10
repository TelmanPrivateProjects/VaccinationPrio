"""Lambda (admin): distribute stored free vaccination slots to waiting people."""
import os

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
datesTableM = dynamodb.Table('datesTableM')
vaccTableM = dynamodb.Table('vaccTableM')
ses = boto3.client('ses')


def distributeDates(event, context):
    """Hand out stored free slots of a zip code area to the next `n` people.

    Trigger : POST /admin/distributedates, protected by the Cognito authorizer
    Event   : {"PLZ": "<zip code>", "n": <number of people>}
    Flow    : walks through the free dates of the zip code in datesTableM and
              books slots for people without an appointment (priority order)
              until `n` people are served. Fully used dates are deleted, a partly
              used date keeps its remaining slots. Every booking sends an e-mail.
    """

    try:

        plz = event["PLZ"]
        n = event["n"]
        i = 0

        # Eligible people (groups 1-3, so people under 18 with group -1 are
        # excluded) without an appointment, in priority order (PLZ-index sort key)
        responseVacc = vaccTableM.query(
            IndexName='PLZ-index',
            Select='ALL_PROJECTED_ATTRIBUTES',
            KeyConditionExpression=Key('PLZ').eq(
                plz) & Key('Priorisierungsgruppe').between(1, 3),
            FilterExpression="attribute_not_exists(Termin)")

        # Free slots of this zip code, ordered by day (Datum sort key)
        responseDates = datesTableM.query(
            KeyConditionExpression=Key('PLZ').eq(plz))

        entries = responseVacc["Items"]
        dates = responseDates["Items"]

        # Never book more people than are waiting
        if n > len(entries):
            n = len(entries)

        # Walk through the days and book slots until n people are served.
        # A fully used day is deleted; a partly used day keeps its remaining slots.
        for date in dates:
            if n <= 0:
                break
            slots = list(date["Termine"])
            used, remaining = slots[:n], slots[n:]

            for time in used:
                addDateToPerson(
                    entries[i]["ID"], entries[i]["Mail"], date["Datum"], time)
                i = i + 1
            n = n - len(used)

            if remaining:
                datesTableM.update_item(
                    Key={
                        'PLZ': plz,
                        'Datum': date["Datum"],
                    },
                    UpdateExpression="SET Termine = :t",
                    ExpressionAttributeValues={
                        ':t': remaining
                    },
                    ReturnValues="UPDATED_NEW"
                )
            else:
                datesTableM.delete_item(
                    Key={'PLZ': plz, 'Datum': date["Datum"]}
                )

        return "Dates distributed!"
    except KeyError as e:
        return "Something went wrong ..."


# Book a slot for one person (vaccTableM.Termin) and notify them by e-mail via SES
def addDateToPerson(id, mail, date, time):

    vaccTableM.update_item(
        Key={
            'ID': id
        },
        UpdateExpression="SET Termin = :t",
        ExpressionAttributeValues={
            ':t': date+"-"+time
        },
        ReturnValues="UPDATED_NEW"
    )

    ses.send_email(
        Source=os.environ['SENDER_EMAIL'],
        Destination={
            'ToAddresses': [
                mail
            ]
        },
        Message={
            'Subject': {
                'Data': 'Impftermin',
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': "Ihr Impftermin ist am "+date+", um "+time+" Uhr.",
                    'Charset': 'utf-8'
                }
            }
        }
    )
