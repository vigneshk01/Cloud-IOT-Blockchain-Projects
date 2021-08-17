import logging
from model import IOTAggregatorModel, GenerateAlertsModel, IOTDataGeneratorModel

# Change the below step value between 1 & 8 to run the specific scenario (some steps are optional):
step = 8

if step == 1:
    # -----Optional -------  To create a table named "bsm_data"
    DataModel = IOTDataGeneratorModel()
    resp = DataModel.create_new_table('bsm_data', 'deviceid', 'timestamp')
    print(resp)

elif step == 2:
    # -----Optional -------  Created for testing purpose only - to insert json dump into local "bsm_data" table
    DataModel = IOTDataGeneratorModel()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
    resp = DataModel.load_json_data('bsm_data', './export.json')
    if resp:
        print(resp)

elif step == 3:
    # +++++ Required +++++  Created a GSI "datatype-index" with datatype as "partition_key" and used it for querying the data
    DataModel = IOTDataGeneratorModel()
    resp = DataModel.create_gsi_fn('bsm_data', 'datatype-index', 'datatype')
    print(resp)

elif step == 4:
    # -----Optional -------  created for '--------DELETING-------' the index previously created index
    DataModel = IOTDataGeneratorModel()
    resp = DataModel.delete_gsi_fn('bsm_data', 'datatype-index', 'datatype')
    print(resp)

elif step == 5:
    # +++++ Required +++++  To create the aggregate table "bsm_aggr_data" for storing aggregated_values
    aggr_model = IOTAggregatorModel()
    resp = aggr_model.create_aggr_table('bsm_aggr_data', 'datatype', 'start_timestamp')
    print(resp)

elif step == 6:
    # +++++ Required +++++  To generate and insert the aggregated data per minute into "bsm_agg_data" table
    aggr_model = IOTAggregatorModel()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
    resp = aggr_model.generate_sensor_aggr_data_per_min('bsm_data', 'datatype-index', 'bsm_aggr_data',
                                                        '2021-03-21 16:00:00',
                                                        '2021-03-21 17:00:00')
    print(resp)

elif step == 7:
    # -----Optional ------- To create a table named "bsm_agg_data" for storing the alerts
    alerts_model = GenerateAlertsModel()
    resp = alerts_model.create_new_table('bsm_alerts', 'datatype', 'timestamp')
    print(resp)

elif step == 8:
    # +++++ Required +++++  Reads the rules.json file and finds anomalies and inserts into bsm_alerts table
    alerts_model = GenerateAlertsModel()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
    resp = alerts_model.monitor_db('rules.json', 'bsm_aggr_data')
    print(resp)
