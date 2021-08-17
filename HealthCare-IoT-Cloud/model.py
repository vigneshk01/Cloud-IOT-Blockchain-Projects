import json
import time
import logging
import pandas as pd
from decimal import Decimal
from database import Database
from datetime import datetime, timedelta


class IOTDataGeneratorModel:
    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.result_list = []

    @property
    def latest_error(self):
        return self._latest_error

    @staticmethod
    def json_read(fpath):
        with open(fpath, 'r') as fr:
            tr = json.load(fr, parse_float=Decimal)
        return tr

    def create_new_table(self, table_name, partition_key, sort_key):
        schema = [
            {'AttributeName': partition_key, 'KeyType': 'HASH'},
            {'AttributeName': sort_key, 'KeyType': 'RANGE'}
        ]
        attributes = [
            {'AttributeName': partition_key, 'AttributeType': 'S'},
            {'AttributeName': sort_key, 'AttributeType': 'S'}
        ]
        throughput = {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        resp = self._db.create_table(table_name, schema, attributes, throughput)
        return resp

    # for testing purpose only
    def load_json_data(self, table_name, file_path):
        json_resp = self.json_read(file_path)
        for device in json_resp:
            value = Decimal(list(device['value'].values())[0])
            deviceid = list(device['deviceid'].values())[0]
            timestamp = list(device['timestamp'].values())[0]
            datatype = list(device['datatype'].values())[0]

            # Due to 25 items per batch limit, in local dynamodb, i am using the single insert query
            param = {
                'Item': {
                    'deviceid': deviceid,
                    'timestamp': timestamp,
                    'datatype': datatype,
                    'value': value
                }
            }
            resp = self._db.put_single_item(table_name, **param)
            logging.info(resp)

    def create_gsi_fn(self, table_name, index_name, index_attr):
        attributes = [
            {'AttributeName': index_attr, 'AttributeType': 'S'}
        ]
        gsi_conf = [
            {
                'Create': {
                    "IndexName": index_name,
                    "KeySchema": [
                        {"AttributeName": index_attr, "KeyType": "HASH"}
                    ],
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    },
                    "Projection": {
                        "ProjectionType": "ALL"
                    }
                }
            }
        ]
        resp = self._db.gsi_schema(table_name, attributes, gsi_conf)
        if 'updated' in resp:
            return 'GlobalSecondaryIndex created successfully for "{0}" with "{1}"'.format(table_name, index_name)
        else:
            return resp

    def delete_gsi_fn(self, table_name, index_name, index_attr):
        attributes = [
            {'AttributeName': index_attr, 'AttributeType': 'S'}
        ]
        gsi_conf = [
            {'Delete': {"IndexName": index_name}
             }
        ]
        resp = self._db.gsi_schema(table_name, attributes, gsi_conf)
        if 'updated' in resp:
            return 'GlobalSecondaryIndex {1} deleted successfully for "{0}"'.format(table_name, index_name)
        else:
            return resp


class IOTAggregatorModel:

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.result_list = []

    @property
    def latest_error(self):
        return self._latest_error

    def create_aggr_table(self, table_name, partition_key, sort_key):
        schema = [
            {'AttributeName': partition_key, 'KeyType': 'HASH'},
            {'AttributeName': sort_key, 'KeyType': 'RANGE'}
        ]
        attributes = [
            {'AttributeName': partition_key, 'AttributeType': 'S'},
            {'AttributeName': sort_key, 'AttributeType': 'S'}
        ]
        throughput = {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        resp = self._db.create_table(table_name, schema, attributes, throughput)
        return resp

    def generate_sensor_aggr_data_per_min(self, table_name, index_name, agg_table_name, start_date, end_date):
        sensor_lst = ['HeartRate', 'Temperature', 'SPO2']

        for sensor in sensor_lst:
            logging.info(sensor)
            startdate = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            enddate = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

            startminute = startdate
            nextminute = startdate + timedelta(minutes=1)

            while nextminute <= enddate:
                param = {
                    "IndexName": index_name,
                    "ProjectionExpression": '#val',
                    "KeyConditionExpression": 'datatype= :dt',
                    "ExpressionAttributeNames": {'#val': 'value', '#ts': 'timestamp'},
                    "FilterExpression": '#ts between :timestampStart AND :timestampEnd',
                    "ExpressionAttributeValues": {':dt': sensor, ':timestampStart': str(startminute),
                                                  ':timestampEnd': str(nextminute)}
                }
                resp = self._db.query_table(table_name, **param)
                if 'Items' in resp:
                    logging.info(resp['Items'])
                    resp_result_lst = list([d['value'] for d in resp['Items']])
                    if resp_result_lst:
                        sensor_min = min(resp_result_lst)
                        sensor_max = max(resp_result_lst)
                        sensor_avg = sum(resp_result_lst) / len(resp_result_lst)

                        param2 = {
                            "Item": {'datatype': sensor, 'start_timestamp': str(startminute),
                                     'end_timestamp': str(nextminute), 'avg': sensor_avg, 'min': sensor_min,
                                     'max': sensor_max}
                        }
                        self._db.put_single_item(agg_table_name, **param2)

                startminute = nextminute
                nextminute = nextminute + timedelta(minutes=1)
        return 'Data Generated successfully'


class GenerateAlertsModel:

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.result_list = []

    @property
    def latest_error(self):
        return self._latest_error

    @staticmethod
    def json_read(fpath):
        with open(fpath, 'r') as fr:
            tr = json.load(fr)
        return tr

    @staticmethod
    def find_anomalies(res_dict, tc):

        df = pd.DataFrame.from_dict(res_dict)
        df = df.reindex(['start_timestamp', 'datatype', 'min', 'max'], axis='columns')

        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'])
        dt = df['start_timestamp']
        day = pd.Timedelta('1m')

        in_block = ((dt - dt.shift(-1)).abs() == day) | (dt.diff() == day)
        filt = df.loc[in_block]

        breaks = filt['start_timestamp'].diff() != day
        groups = breaks.cumsum()

        c = filt.copy()
        c['groups'] = groups
        c['groups'].value_counts(dropna=False)

        ndf = c[c['groups'].map(c['groups'].value_counts()) >= int(tc)]
        final = ndf.drop_duplicates('groups', keep='last')
        result = final.to_dict('records')
        return result

    def create_new_table(self, table_name, partition_key, ts):
        schema = [{'AttributeName': partition_key, 'KeyType': 'HASH'}, {'AttributeName': ts, 'KeyType': 'RANGE'}]
        attributes = [{'AttributeName': partition_key, 'AttributeType': 'S'},
                      {'AttributeName': ts, 'AttributeType': 'S'}]
        throughput = {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        resp = self._db.create_table(table_name, schema, attributes, throughput)
        return resp

    def query_aggr_table(self, aggr_table, sensor, min_val, max_value):
        param = {
            "ProjectionExpression": '#ts,#dt,#min,#max',
            "KeyConditionExpression": 'datatype= :dt',
            "ExpressionAttributeNames": {'#ts': 'start_timestamp', '#dt': 'datatype', '#min': 'min', '#max': 'max'},
            "FilterExpression": '#min < :minvalue or #max > :maxvalue',
            "ExpressionAttributeValues": {':dt': sensor, ':minvalue': min_val, ':maxvalue': max_value}
        }
        resp = self._db.query_table(aggr_table, **param)
        return resp

    def monitor_db(self, filepath, aggr_table):
        try:
            while 1 == 1:
                json_data = self.json_read(filepath)
                if 'rules' in json_data:
                    rules_lst = json_data['rules']
                    for rule in rules_lst:
                        triggerCount = rule['triggerCount']
                        resp = self.query_aggr_table(aggr_table, rule['datatype'], rule['min'], rule['max'])
                        if resp['Items']:
                            resp_dict = resp['Items']
                            anomaly_op = self.find_anomalies(resp_dict, triggerCount)
                            if anomaly_op:
                                for i in anomaly_op:
                                    logging.info(
                                        'New anomalies detected for sensor-type: {1} at {0}, the data exceeded the threshold limit set!!!. \n Following are the values observed for that duration: \n avg_min: {2} \n avg_max: {3} \n\n'.format(
                                            i['start_timestamp'], i['datatype'], i['min'], i['max']))
                                    param = {
                                        "Item": {
                                            'timestamp': str(i['start_timestamp']),
                                            'datatype': i['datatype'],
                                            'avg_min': i['min'],
                                            'avg_max': i['max']
                                        }
                                    }
                                    self._db.put_single_item('bsm_alerts', **param)
                logging.info('\nThe program will recheck for anomalies again in 5 minutes .....')
                time.sleep(180)
        except KeyboardInterrupt:
            return 'Program aborted'
