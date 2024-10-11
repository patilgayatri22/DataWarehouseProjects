# -*- coding: utf-8 -*-
"""DataWarehouse_Homework5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15brYhwiuCHpOxFqNdjoLQwluQbD7Dw3x
"""

# In Cloud Composer, add snowflake-connector-python to PYPI Packages
from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.utils.dates import days_ago
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
import snowflake.connector
import requests
import json
from datetime import datetime, timedelta


def return_snowflake_conn():
      # Establish a connection to Snowflake
      conn = snowflake.connector.connect(
          user=Variable.get('snowflake_user'),
          password=Variable.get('snowflake_password'),
          account=Variable.get('account'),
          warehouse='compute_wh',
          database='dev_db',
          schema='raw_data',
          role='accountadmin'
      )
      # Create a cursor object
      return conn.cursor()


@task
def return_last_90d_price():
    """
    - return the last 90 days of the stock prices of symbol as a list of json strings
    """
    vantage_api_key = Variable.get('vantage_api_key')
    symbol= "COST"

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={vantage_api_key}'
    r = requests.get(url)
    data = r.json()
    symbol_value = data["Meta Data"]["2. Symbol"]
    results = []   # empyt list for now to hold the 90 days of stock info (open, high, low, close, volume)
    presentday  = datetime.now().date()
    begin_date = presentday - timedelta(days=90)

    for d in data["Time Series (Daily)"]:   # here d is a date: "YYYY-MM-DD"
        stock_info = data["Time Series (Daily)"][d]
        start_date = datetime.strptime(d,'%Y-%m-%d').date()
        if begin_date <= start_date <= presentday:
          stock_info["date"] = d
          stock_info["symbol"] = symbol_value
          results.append(stock_info)

    return results



@task
def load_v2(results):
      conn = return_snowflake_conn()
      target_table = "dev_db.raw_data.stock_price"
      try:
            conn.execute(f"""
                    CREATE OR REPLACE TABLE {target_table}  (
                        date DATE  PRIMARY KEY NOT NULL,
                        open DECIMAL(10, 2),
                        high DECIMAL(10, 2),
                        low DECIMAL(10, 2),
                        close DECIMAL(10, 2),
                        volume BIGINT,
                        symbol VARCHAR(10) NOT NULL
                            );
                      """)

            # Insert records into the staging table
            for r in results:
              open = r["1. open"]
              high = r["2. high"]
              low = r["3. low"]
              close = r["4. close"]
              volume = r["5. volume"]
              date=r['date']
              symbol=r['symbol']
              insert_sql = f"INSERT INTO {target_table} (date, open, high, low, close, volume, symbol) VALUES ('{date}',{open}, {high}, {low}, {close}, {volume}, '{symbol}')"
              conn.execute(insert_sql)

            conn.execute("COMMIT;")
            print(f"Data loaded correctly in Target table: '{target_table}' !")
      except Exception as e:
            print(e)
            conn.execute("ROLLBACK;")
            raise e

with DAG(
    dag_id = 'ReadStockPriceData',
    start_date = datetime(2024,10,10),
    catchup=False,
    tags=['ETL'],
    schedule = '@daily'
) as dag:
  read_90days_stockdata=return_last_90d_price()
  load_v2(read_90days_stockdata)