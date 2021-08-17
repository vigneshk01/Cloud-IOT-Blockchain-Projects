import json
import boto3
import base64
import datetime
from decimal import Decimal

client = boto3.client('sns')
db_res = boto3.resource('dynamodb')
snsTopic = 'arn:aws:sns:us-east-1:428938486474:lambda_stock_trigger'
msg_subject = 'Alert - Stock Threshold Breach Trigger'
table_name = 'StockAlerts'


# func to calculate percentage
def percentage(percent, whole):
    return (percent * whole) / 100.0


# func for reading from dynamoDB
def query_item(tbl_name, **params):
    table = db_res.Table(tbl_name)
    resp = table.query(**params)
    return resp


# func for writing to dynamoDB
def put_single_item(tbl_name, **params):
    table = db_res.Table(tbl_name)
    resp = table.put_item(**params)
    return resp


# triggered on kinesis event, decodes the kinesis data and converts the data to the specific requirement.
def lambda_handler(event, context):
    try:
        for record in event['Records']:

            payload = base64.b64decode(record["kinesis"]["data"])
            data = json.loads(payload)

            fiftyTwo_weekHigh = data["52WeekHigh"]
            fiftyTwo_weekLow = data["52WeekLow"]
            curr_price = data["current price"]
            stock_name = data["stock-id"]
            stock_timestamp = data["timestamp"]
            timestamp = str(datetime.datetime.now().isoformat())

            today = datetime.datetime.today()
            today = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 0).isoformat()

            tomorrow = datetime.datetime.today() + datetime.timedelta(1)
            tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, 0).isoformat()
            param = {}

            # Apply percentage to find threshold and verify the business logic criteria
            high_trigger_threshold = percentage(80, fiftyTwo_weekHigh)
            low_trigger_threshold = percentage(120, fiftyTwo_weekLow)

            if curr_price >= high_trigger_threshold or curr_price <= low_trigger_threshold:
                if curr_price >= high_trigger_threshold:
                    flag = '52WeekHigh'
                    flag_price = fiftyTwo_weekHigh
                else:
                    flag = '52WeekLow'
                    flag_price = fiftyTwo_weekLow

                # based on the above outcome, create the db query and verify the data finally write to dynamodb.
                param["ProjectionExpression"] = '#val'
                param["KeyConditionExpression"] = 'stock_name= :sk AND #ts between :timestampStart AND :timestampEnd'
                param["ExpressionAttributeNames"] = {'#val': 'stock_name', '#ts': 'timestamp'}
                param["ExpressionAttributeValues"] = {':sk': stock_name, ':timestampStart': str(today),
                                                      ':timestampEnd': str(tomorrow)}
                resp = query_item(table_name, **param)
                print(resp)

                param = {"Item": {}}
                param["Item"]['stock_name'] = stock_name
                param["Item"]['timestamp'] = timestamp
                param["Item"]['stock_timestamp'] = stock_timestamp
                param["Item"]['current_price'] = Decimal(str(curr_price))
                param["Item"]['52WeekLow'] = Decimal(str(fiftyTwo_weekLow))
                param["Item"]['52WeekHigh'] = Decimal(str(fiftyTwo_weekHigh))

                result = put_single_item(table_name, **param)
                print(result)

                # based on the query result, send alert only if data does not exists for the specific stock.
                if not resp['Items']:
                    pretty_data = json.dumps(data, indent=2)

                    msg_body = "\nHello,\n\n{0}'s current Stock price value: {1} is nearing the {2} value of {3}.\n\n{4}\n\n***This is a system generated email, please do not reply back***".format(
                        stock_name, curr_price, flag, flag_price, pretty_data)

                    resp = client.publish(TopicArn=snsTopic, Message=msg_body, Subject=msg_subject)
                    print(resp)

    except Exception as e:
        print(e)
        return e
