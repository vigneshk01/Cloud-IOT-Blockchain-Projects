import boto3

kinesis = boto3.client('kinesis', region_name="us-east-1")
stream_name = 'Cloud-Project1-Data-Stream'

response = kinesis.describe_stream(StreamName=stream_name, Limit=1)
shard_id = response['StreamDescription']['Shards'][0]['ShardId']

response = kinesis.get_shard_iterator(StreamName=stream_name, ShardId=shard_id, ShardIteratorType='TRIM_HORIZON')
shard_iterator = response['ShardIterator']

while shard_iterator:
    response = kinesis.get_records(ShardIterator=shard_iterator, Limit=1)

    if not response['Records']:
        break

    print(response['Records'][0]['Data'])
    next_iterator = response['NextShardIterator']
    shard_iterator = next_iterator
