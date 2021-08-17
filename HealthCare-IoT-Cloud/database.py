import boto3
from botocore.exceptions import ClientError


class Database:
    HOST = 'http://localhost:8004'
    # HOST = 'https://dynamodb.us-east-1.amazonaws.com'

    def __init__(self):
        self._db_conn = boto3.resource('dynamodb', endpoint_url=Database.HOST)
        self._db_client = boto3.client('dynamodb', endpoint_url=Database.HOST)

    def query_table(self, table_name, **params):
        table = self._db_conn.Table(table_name)
        response = table.query(**params)
        return response

    def put_single_item(self, table_name, **params):
        table = self._db_conn.Table(table_name)
        response = table.put_item(**params)
        return response

    def create_table(self, table_name, ks, attrib_def, pt):
        try:
            table = self._db_conn.create_table(
                TableName=table_name,
                KeySchema=ks,
                AttributeDefinitions=attrib_def,
                ProvisionedThroughput=pt
            )
            # Wait until the table exists.
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            return 'Table "{0}" created successfully'.format(table_name)

        except ClientError as e:
            return ' Skipped due to exception ', e.response['Error']['Code']

    def gsi_schema(self, table_name, attrib_def, gsi):
        try:
            resp = self._db_client.update_table(
                TableName=table_name,
                AttributeDefinitions=attrib_def,
                GlobalSecondaryIndexUpdates=gsi)

            if resp:
                return 'GlobalSecondaryIndex updated successfully'

        except ClientError as e:
            return ' Skipped due to exception ', e.response['Error']['Code']

    def update_single_item(self, table_name, **params):
        table = self._db_conn.Table(table_name)
        response = table.update_item(**params)
        return response
