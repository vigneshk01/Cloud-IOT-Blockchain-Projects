Steps and notes:

Use Below commands to generate the data for two devices:
Bot1
python BedSideMonitor.py -d "HealthBot01" -e a41zh0v268phg-ats.iot.us-east-1.amazonaws.com -r ./HealthBot01/AmazonRootCA1.pem -c ./HealthBot01/31c54034f3-certificate.pem.crt -k ./HealthBot01/31c54034f3-private.pem.key -id "device1" -t iot/bsm

Bot 2
python BedSideMonitor.py -d "HealthBot02" -e a41zh0v268phg-ats.iot.us-east-1.amazonaws.com -r ./HealthBot02/AmazonRootCA1.pem -c ./HealthBot02/87cba729b2-certificate.pem.crt -k ./HealthBot02/87cba729b2-private.pem.key -id "device2" -t iot/bsm

The bsm_data was already created with "deviceid" as Partition_Key and timestamp as Sort_key ,hence i decided to create a GSI "datatype-index" with datatype as "partition_key" and timestamp as "sort_key" (implementation provided in the code)

Use the main.py to run all the scenarios


Notes:
start_timestamp is considered as the sort_key in most of the tables
timestamp in BSM_alerts table is nothing but the start_timestamp of bsm_aggr_data table