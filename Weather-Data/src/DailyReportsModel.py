import logging
from datetime import datetime
import pymongo
from src.database import Database


class DailyReportModel:
    WEATHER_DATA_COLLECTION = 'weather_data'
    DAILY_REPORTS_COLLECTION = 'daily_reports'

    def __init__(self):
        self._db = Database()
        self._latest_error = ''
        self.result_list = []

    @property
    def latest_error(self):
        return self._latest_error

    def buildQuery(query={}):
        agg_query = [
            {'$match': query
             }, {'$group': {
                '_id': {
                    'date': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$timestamp'
                        }
                    }, 'device_id': '$device_id'
                }, 'min': {
                    '$min': '$value'
                }, 'max': {
                    '$max': '$value'
                }, 'avg': {
                    '$avg': '$value'
                }}
            }, {'$project': {
                '_id': 0,
                '_device_id': '$_id.device_id',
                '_date': '$_id.date',
                '_avg': '$avg',
                '_min': '$min',
                '_max': '$max'
            }
            }, {'$project': {
                '_id': 0,
                'device_id': '$_device_id',
                'date': '$_date',
                'avg': '$_avg',
                'min': '$_min',
                'max': '$_max'
            }
            }, {'$sort': {
                'device_id': 1,
                'date': 1
            }
            }
        ]
        return agg_query

    def insert_aggregated_data(self, weather_aggr):
        idx_fields = ('device_id', pymongo.ASCENDING), ('date', pymongo.ASCENDING)
        uniqueness = True

        self._db.create_index_onColl(DailyReportModel.DAILY_REPORTS_COLLECTION, idx_fields, uniqueness)
        lst_aggr = list(weather_aggr)

        for x in lst_aggr:
            try:
                key = {'device_id': x['device_id'], 'date': datetime.strptime(x['date'], '%Y-%m-%d'),
                       'average': x['avg'], 'minimum': x['min'], 'maximum': x['max']}
                inserted_obj = self._db.insert_single_data(DailyReportModel.DAILY_REPORTS_COLLECTION, key)
                logging.debug("object_id: %s, Device_id: %s, timestamp:%s" % (inserted_obj, x['device_id'], x['date']))
                self.result_list.append("object_id: %s for Device_id: %s, timestamp:%s" % (
                    inserted_obj, x['device_id'], x['date']))
            except pymongo.errors.DuplicateKeyError:
                # logging.warning("An entry for this device %s on this date %s already exists" % (x['device_id'], x['date']))
                self.result_list.append(
                    "An entry for this device %s on this date %s already exists" % (x['device_id'], x['date']))
                continue
        return "\n".join(self.result_list)

    def generate_bulk_aggr(self):
        weather_aggr_result = self._db.generate_aggregate(DailyReportModel.WEATHER_DATA_COLLECTION,
                                                          DailyReportModel.buildQuery())
        logging.debug(weather_aggr_result)
        result_data = DailyReportModel.insert_aggregated_data(self, weather_aggr_result)
        return result_data

    def generate_aggr_by_dev_and_date(self, device_id, frmdate, todate):
        frmdate = datetime.strptime(frmdate, '%Y-%m-%d')
        todate = datetime.strptime(todate, '%Y-%m-%d')
        query = {'device_id': device_id, 'timestamp': {'$gt': frmdate, '$lt': todate}}

        weather_aggr_result = self._db.generate_aggregate(DailyReportModel.WEATHER_DATA_COLLECTION,
                                                          DailyReportModel.buildQuery(query))
        # logging.warning(weather_aggr_result)
        if len(list(weather_aggr_result)) == 0:
            self._latest_error = f'Weather data does not exists for {device_id}'
            return -1
        # logging.warning(list(weather_aggr_result))
        result_data = DailyReportModel.insert_aggregated_data(self, weather_aggr_result)
        return result_data

    def find_by_dev_id_and_date(self, device_id, frmdate, todate):
        frmdate = datetime.strptime(frmdate, '%Y-%m-%d')
        todate = datetime.strptime(todate, '%Y-%m-%d')
        query = {'device_id': device_id, 'date': {'$gte': frmdate, '$lt': todate}}
        query_result = self._db.get_all_data(DailyReportModel.DAILY_REPORTS_COLLECTION, query)

        if not query_result:
            self._latest_error = f'No data for {device_id} exists'
            return -1

        for x in query_result:
            self.result_list.append("Device ID: %s \n  Date: %s \n  Average: %s \n  Minimum: %s \n  Maximum: %s" % (
                x['device_id'], x['date'], x['average'], x['minimum'], x['maximum']))
        return "\n".join(self.result_list)
