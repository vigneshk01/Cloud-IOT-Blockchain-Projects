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


def percentage(percent, whole):
    return (percent * whole) / 100.0


def query_item(tbl_name, **params):
    table = db_res.Table(tbl_name)
    resp = table.query(**params)
    return resp


def put_single_item(tbl_name, **params):
    table = db_res.Table(tbl_name)
    resp = table.put_item(**params)
    return resp


def lambda_handler(event):
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

            high_trigger_threshold = percentage(80, fiftyTwo_weekHigh)
            low_trigger_threshold = percentage(120, fiftyTwo_weekLow)

            # print('Stock Name      : {0}'.format(stock_name))
            # print('Current Price   : {0}'.format(curr_price))
            # print('52WeekHigh      : {0}'.format(fiftyTwo_weekHigh))
            # print('52WeekLow       : {0}'.format(fiftyTwo_weekLow))
            # print('HigherThreshold : {0}'.format(high_trigger_threshold))
            # print('LowerThreshold  : {0}'.format(low_trigger_threshold))

            if curr_price >= high_trigger_threshold or curr_price <= low_trigger_threshold:
                if curr_price >= high_trigger_threshold:
                    flag = '52WeekHigh'
                    flag_price = fiftyTwo_weekHigh
                else:
                    flag = '52WeekLow'
                    flag_price = fiftyTwo_weekLow

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

                if not resp['Items']:
                    pretty_data = json.dumps(data, indent=2)

                    msg_body = "\nHello,\n\n{0}'s current Stock price value: {1} is nearing the {2} value of {3}.\n\n{4}\n\n***This is a system generated email, please do not reply back***".format(
                        stock_name, curr_price, flag, flag_price, pretty_data)

                    resp = client.publish(TopicArn=snsTopic, Message=msg_body, Subject=msg_subject)
                    print(resp)

    except Exception as e:
        print(e)
        return e


test = {
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49590338271490256608559692538361571095921575989136588898",
                "data": "eyAidGltZXN0YW1wIjogIjIwMjEtMDUtMDdUMTg6MzA6MDAuMDAwWiIsICJzdG9jay1pZCI6ICJNU0ZUIiwgImN1cnJlbnQgcHJpY2UiOiAyNDYuNzU5OTk0NTA2OCwgIjUyV2Vla0hpZ2giOiAyNjMuMTksICI1MldlZWtMb3ciOiAxNzUuNjh9",
                "approximateArrivalTimestamp": 1545084650.987
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49590338271490256608559692538361571095921575989136588898",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::123456789012:role/lambda-kinesis-role",
            "awsRegion": "us-east-2",
            "eventSourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/Cloud-Project1-Data-Stream"
        }, {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49590338271490256608559692538361571095921575989136588898",
                "data": "eyAidGltZXN0YW1wIjogIjIwMjEtMDUtMDhUMTg6MzA6MDAuMDAwWiIsICJzdG9jay1pZCI6ICJNU0ZUIiwgImN1cnJlbnQgcHJpY2UiOiAyNDYuNzU5OTk0NTA2OCwgIjUyV2Vla0hpZ2giOiAyNjMuMTksICI1MldlZWtMb3ciOiAxNzUuNjh9",
                "approximateArrivalTimestamp": 1545084650.987
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49590338271490256608559692538361571095921575989136588898",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::123456789012:role/lambda-kinesis-role",
            "awsRegion": "us-east-2",
            "eventSourceARN": "arn:aws:kinesis:us-east-1:123456789012:stream/Cloud-Project1-Data-Stream"
        }
    ]
}
lambda_handler(test)
