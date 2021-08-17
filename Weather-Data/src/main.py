import logging
from datetime import datetime
from DailyReportsModel import DailyReportModel
from model import UserModel, DeviceModel, WeatherDataModel

# Shows how to initiate and search in the users collection based on a username
session_user = 'user_!'
user_coll = UserModel(session_user)
user_document = user_coll.find_by_username('user_1')
if user_document == -1:
    print(user_coll.latest_error)
else:
    print(user_document)

# Shows how to initiate and search in the users collection based on Object_id
session_user = 'admin'
user_coll = UserModel(session_user)
user_document = user_coll.find_by_object_id('600f50e98b639b310e57177f')
if user_document == -1:
    print(user_coll.latest_error)
else:
    print(user_document)

# Shows a successful attempt on how to insert a user
session_user = 'admin'
user_coll = UserModel(session_user)
user_document2 = user_coll.insert('test_5', 'test_3@example.com', 'default')
if user_document2 == -1:
    print(user_coll.latest_error)
else:
    print(user_document2)

# Shows how to initiate and search in the devices collection based on a device id
session_user = 'user_4'
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
device_coll = DeviceModel(session_user)
device_document1 = device_coll.find_by_device_id('DT002')
if device_document1 == -1:
    print(device_coll.latest_error)
else:
    print(device_document1)

# Shows how to initiate and search in the users collection based on Object_id
session_user = 'user_8'
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
device_coll = DeviceModel(session_user)
device_document1 = device_coll.find_by_object_id('600f50e98b639b310e571784')
if device_document1 == -1:
    print(device_coll.latest_error)
else:
    print(device_document1)

# Shows a successful attempt on how to insert a new device
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
session_user = 'user_2'
device_coll = DeviceModel(session_user)
device_document = device_coll.insert('DT230', 'Temperature Sensor', 'Temperature', 'Acme')
if device_document == -1:
    print(device_coll.latest_error)
else:
    print(device_document)

# Shows how to initiate and search in the weather_data collection based on a device_id and timestamp
session_user = 'user_2'
wdata_coll = WeatherDataModel(session_user)
wdata_document1 = wdata_coll.find_by_device_id_and_timestamp('DT004', datetime(2020, 12, 2, 13, 30, 0))
if wdata_document1 == -1:
    print(wdata_coll.latest_error)
else:
    print(wdata_document1)

# Shows how to initiate and search in the weather_data collection based on a device_id and timestamp
session_user = 'user_4'
wdata_coll = WeatherDataModel(session_user)
wdata_document1 = wdata_coll.find_by_object_id('600f50e98b639b310e57178d')
if wdata_document1 == -1:
    print(wdata_coll.latest_error)
else:
    print(wdata_document1)

# Inserts data into weather_data collection based on user_role device_id access_type
session_user = 'user_3'
wdata_coll = WeatherDataModel(session_user)
# Shows a failed attempt on how to insert a new data point
wdata_document = wdata_coll.insert('DT002', 12, datetime(2020, 12, 2, 13, 30, 0))
if wdata_document == -1:
    print(wdata_coll.latest_error)
else:
    print(wdata_document)

# The below function call generates aggregates 'min' 'max' 'avg' temperature for existing weather_data
drep_coll = DailyReportModel()
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
daily_rep_doc = drep_coll.generate_bulk_aggr()
print(daily_rep_doc)

# The below function generates - aggregates 'min' 'max' 'avg' temperature from existing weather_data for a defined time_period and stores under daily_reports collection
drep_coll = DailyReportModel()
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
daily_rep_doc = drep_coll.generate_aggr_by_dev_and_date("DT002", "2020-12-01", "2020-12-02")
if daily_rep_doc == -1:
    print(drep_coll.latest_error)
else:
    print(daily_rep_doc)

# The below function fetches and displays the aggregated daily_reports of a given device_id for a defined time period
drep_coll = DailyReportModel()
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(funcName)s %(message)s')
daily_rep_doc = drep_coll.find_by_dev_id_and_date("DT002", "2020-12-01", "2020-12-02")
if daily_rep_doc == -1:
    print(drep_coll.latest_error)
else:
    print(daily_rep_doc)
