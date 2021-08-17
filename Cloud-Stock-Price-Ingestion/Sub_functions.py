import datetime

import boto3

stream_name = 'Cloud-Project1-Data-Stream'
kinesis = boto3.client('kinesis', region_name="us-east-1")  # Modify this line of code according to your requirement.
lambdac = boto3.client('lambda')


def create_stream(stm_name):
    resp = kinesis.create_stream(StreamName=stm_name, ShardCount=1)
    return resp


def delete_stream(stm_name):
    resp = kinesis.delete_stream(StreamName=stm_name, EnforceConsumerDeletion=True)
    return resp


def event_create():
    resp = lambdac.create_event_source_mapping(
        EventSourceArn='arn:aws:kinesis:us-east-1:428938486474:stream/Cloud-Project1-Data-Stream',
        FunctionName='lambda-for-cloud-project1',
        Enabled=True,
        BatchSize=100,
        MaximumBatchingWindowInSeconds=5,
        StartingPosition='LATEST',
        MaximumRetryAttempts=0)
    return resp['UUID']


def event_update(UID, flg):
    resp = lambdac.update_event_source_mapping(
        UUID=UID,
        FunctionName='lambda-for-cloud-project1',
        Enabled=flg,
        BatchSize=100,
        MaximumBatchingWindowInSeconds=5,
        DestinationConfig={
            # 'OnSuccess': {'Destination': 'arn:aws:sns:us-east-1:428938486474:lambda_stock_trigger'}
            'OnFailure': {'Destination': 'arn:aws:sns:us-east-1:428938486474:lambda_stock_trigger'}
        },
        BisectBatchOnFunctionError=False,
        MaximumRetryAttempts=0)
    return resp


def list_event():
    resp = lambdac.list_event_source_mappings(
        EventSourceArn='arn:aws:kinesis:us-east-1:428938486474:stream/Cloud-Project1-Data-Stream',
        FunctionName='lambda-for-cloud-project1',
        MaxItems=10)
    return resp['EventSourceMappings'][0]['UUID']


# response = create_stream(stream_name)
# print(response)

# response = list_event()
# print(response)

# response = event_create()
# print(response)

# flag = True
# UUID = '341666e5-3b53-492d-a15c-aa17e4fdc7f4'
# response = event_update(UUID, flag)
# print(response)

# response = delete_stream(stream_name)
# print(response)
#
# stockid = '200'
# timestamp = '2021-05-03 09:30:00-04:00'
# curr_value = '150.839996'
# fiftyTwoWeekHigh = '200'
# fiftyTwoWeekLow = '100'
# print("{0},{1}{2},{3},{4}".format(stockid, timestamp, curr_value, fiftyTwoWeekHigh, fiftyTwoWeekLow))
# test_rec = {'this': 'is', 'a': 'test'}


# for stock in stocks_to_fetch:
#     data = yf.download(stock, start=yesterday, end=today, interval='1h')
#     flex = data[["Close"]]
#     flex.insert(0, 'Stock-id', stock)
#     flex = flex.copy(deep=False)
#     flex.reset_index(level=0, inplace=True)
#     flex.rename(columns={'index': 'timestamp', 'Close': 'price'}, inplace=True)
#
#     ticker = yf.Ticker(stock)
#     flex['52WeekHigh'] = ticker.info['fiftyTwoWeekHigh']
#     flex['52WeekLow'] = ticker.info['fiftyTwoWeekLow']
#
#     result = flex.to_json(orient='records', date_format='iso')
#     parsed = json.loads(result)
#     data_to_push = json.dumps(parsed, indent=2)
#     print(data_to_push)
#
#     with open(json_file, 'w') as fin:
#         fin.write(data_to_push)
#
#     response = kinesis.put_record(StreamName=stream_name, Data=data_to_push, PartitionKey='1')
#     print(response)
#     time.sleep(5)

timestamp = datetime.datetime.now()
print(timestamp)