import json
import time
import boto3
import datetime
import yfinance as yf

# Your goal is to get per-hour stock price data for a time range for the ten stocks specified in the doc.
# Further, you should call the static info api for the stocks to get their current 52WeekHigh and 52WeekLow values.
# You should craft individual data records with information about the stock-id, price, price timestamp, 52WeekHigh and 52WeekLow values and push them individually on the Kinesis stream

stocks_to_fetch = ('MSFT', 'MVIS', 'GOOG', 'SPOT', 'INO', 'OCGN', 'ABML', 'RLLCF', 'JNJ', 'PSFE')
stream_name = 'Cloud-Project1-Data-Stream'
# json_file = 'temp.json'

kinesis = boto3.client('kinesis', region_name="us-east-1")

# Date Range to Fetch
today = datetime.date.today()
yesterday = datetime.date.today() - datetime.timedelta(1)

# download and loop through all the stocks, and retrieve the selective columns, finally push the data to kinesis stream one after another with a 5-sec delay
for stock in stocks_to_fetch:
    data = yf.download(stock, start=yesterday, end=today, interval='1h')
    flex = data[["Close"]]
    flex.insert(0, 'stock-id', stock)
    flex = flex.copy(deep=False)
    flex.reset_index(level=0, inplace=True)
    flex.rename(columns={'index': 'timestamp', 'Close': 'current price'}, inplace=True)

    ticker = yf.Ticker(stock)
    flex['52WeekHigh'] = ticker.info['fiftyTwoWeekHigh']
    flex['52WeekLow'] = ticker.info['fiftyTwoWeekLow']

    result = flex.to_json(orient='records', date_format='iso')
    parsed = json.loads(result)

    for row in parsed:
        data_to_push = json.dumps(row)
        print(data_to_push)

        # with open(json_file, 'w') as fin:
        #     fin.write(data_to_push)

        response = kinesis.put_record(StreamName=stream_name, Data=data_to_push, PartitionKey='1')
        print(response)
        time.sleep(5)
