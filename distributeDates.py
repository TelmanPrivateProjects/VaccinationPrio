import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
datesTableM = dynamodb.Table('datesTableM')
vaccTableM = dynamodb.Table('vaccTableM')
ses = boto3.client('ses')


def distributeDates(event, context):

    try:

        plz = event["PLZ"]
        n = event["n"]
        i = 0

        # Get all persons and available dates
        responseVacc = vaccTableM.query(
            TableName='vaccTableM',
            IndexName='PLZ-index',
            Select='ALL_PROJECTED_ATTRIBUTES',
            KeyConditionExpression=Key('PLZ').eq(
                plz) & Key('Priorisierungsgruppe').lte(3),
            FilterExpression="attribute_not_exists(Termin)")

        responseDates = vaccTableM.query(
            TableName='datesTableM',
            KeyConditionExpression=Key('PLZ').eq(plz))

        entries = responseVacc["Items"]
        dates = responseDates["Items"]

        # Check if enough people are aviable for distrubuition
        if n > len(entries):
            n = len(entries)

        for date in dates:
            count = len(date["Termine"])
            if(count == n):
                for time in date["Termine"]:
                    addDateToPerson(
                        entries[i]["ID"], entries[i]["Mail"], date["Datum"], time)
                    i = i + 1

                datesTableM.delete_item(
                    Key={'PLZ': plz, 'Datum': date["Datum"]}
                )
                break
            elif(count > n):
                date_copy = date["Termine"]
                for time in date["Termine"]:
                    addDateToPerson(
                        entries[i]["ID"], entries[i]["Mail"], date["Datum"], time)
                    date_copy.remove(time)
                    i = i + 1

                datesTableM.update_item(
                    Key={
                        'PLZ': plz,
                        'Datum': date["Datum"],
                    },
                    UpdateExpression="SET Termine = :t",
                    ExpressionAttributeValues={
                        ':t': date_copy
                    },
                    ReturnValues="UPDATED_NEW"
                )
                break
            else:
                for time in date["Termine"]:
                    addDateToPerson(
                        entries[i]["ID"], entries[i]["Mail"], date["Datum"], time)
                    i = i + 1

                datesTableM.delete_item(
                    Key={'PLZ': plz, 'Datum': date["Datum"]}
                )
                n = n - count

    except KeyError as e:
        return "Something went wrong ..."


# Function to add a date to person and send an email
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
        Source='maximilian.goetz@stud.uni-bamberg.de',
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
