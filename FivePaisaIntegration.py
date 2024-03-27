AppName="5P51505350"
AppSource=22085
UserID="KDBDDkraajE"
Password="DFzv7dKMscE"
UserKey="krBvmN0zGOOIcwemzmOLTBhhrbpLD7xQ"
EncryptionKey="q6ZwmANtPVL545lbs7jlQkJcGvy2iR6O"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYTKMBVGM2TAXZVKBDUWRKZ"
from datetime import datetime,timedelta
import pandas_ta as ta
from py5paisa import FivePaisaClient
import pyotp
import pandas as pd
client=None
def login():
    global client
    cred={
        "APP_NAME":AppName,
        "APP_SOURCE":AppSource,
        "USER_ID":UserID,
        "PASSWORD":Password,
        "USER_KEY":UserKey,
        "ENCRYPTION_KEY":EncryptionKey
        }
    twofa = pyotp.TOTP(totpstr)
    twofa = twofa.now()
    client = FivePaisaClient(cred=cred)
    client.get_totp_session(client_code=51505350,totp=twofa,pin=123456)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())
def get_historical_data(timframe, token, RSIPeriod, Spperios, spmul, atrperiod,symbol):
    global client
    current_time = datetime.now()
    if timframe == "1m":
        delta_minutes = 1
        delta_minutes2 = 2
    elif timframe == "3m":
        delta_minutes = 3
        delta_minutes2 = 6
    elif timframe == "5m":
        delta_minutes = 5
        delta_minutes2 = 10
    elif timframe == "15m":
        delta_minutes = 15
        delta_minutes2 = 30

    desired_time1 = current_time - timedelta(minutes=delta_minutes)
    desired_time1 = desired_time1.replace(second=0)
    desired_time_str1 = desired_time1.strftime('%Y-%m-%d %H:%M:%S')

    desired_time2 = current_time - timedelta(minutes=delta_minutes2)
    desired_time2 = desired_time2.replace(second=0)
    desired_time_str2 = desired_time2.strftime('%Y-%m-%d %H:%M:%S')

    from_time = datetime.now() - timedelta(days=6)
    to_time = datetime.now()
    df = client.historical_data('N', 'D', token, timframe, from_time, to_time)
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    df["RSI"] = ta.rsi(close=df["Close"], length=RSIPeriod)
    df["VWAP"] = ta.vwap(high=df["High"], low=df["Low"], close=df["Close"], volume=df["Volume"])
    colname = f'SUPERT_{int(Spperios)}_{spmul}'
    colname2 = f'SUPERTd_{int(Spperios)}_{spmul}'
    df["Supertrend Values"] = ta.supertrend(high=df['High'], low=df['Low'], close=df['Close'], length=Spperios,
                                            multiplier=spmul)[colname]
    df["Supertrend Signal"] = ta.supertrend(high=df['High'], low=df['Low'], close=df['Close'], length=Spperios,
                                            multiplier=spmul)[colname2]
    df["ATR_VALUE"] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'],length=atrperiod,)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')



    if symbol=="NIFTY":
        df.to_csv('NIFTY.csv', index=False)
    if symbol=="BANKNIFTY":
        df.to_csv('BANKNIFTY.csv', index=False)

    last_3_rows = df.tail(3)
    desired_rows = last_3_rows[
        (last_3_rows['Datetime'] == desired_time_str1) | (last_3_rows['Datetime'] == desired_time_str2)]

    return desired_rows



def get_live_market_feed():
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripData": "ITC"},
    {"Exch": "N", "ExchType": "C", "ScripCode": "2885"}]

    print(client.fetch_market_feed_scrip(req_list_))

def previousdayclose(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    pclose_value = float(responce['Data'][0]['PClose'])
    return pclose_value

def get_open_current_candle(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": code}]
    responce = client.fetch_market_feed_scrip(req_list_)
    print(responce)
    return responce


def get_ltp(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "D", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    last_rate = float(responce['Data'][0].get('LastRate', 0))
    return last_rate

def buy( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def sell( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)
def short( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def cover( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def get_position():
    global client
    responce = client.positions()

    return responce

def get_margin():
    global client
    responce= client.margin()

    if responce:
        net_available_margin =float (responce[0]['NetAvailableMargin'])
        return net_available_margin
    else:
        print("Error: Unable to get NetAvailableMargin")
        return None


def get_active_expiery(symbol):
    response = client.get_expiry("N", symbol)
    expiry_dates = []

    for expiry in response['Expiry']:
        expiry_date_string = expiry['ExpiryDate']
        expiry_date_numeric = int(expiry_date_string.split("(")[1].split("+")[0]) / 1000
        epoch = datetime(1970, 1, 1)
        expiry_datetime = epoch + timedelta(seconds=expiry_date_numeric)
        expiry_date = expiry_datetime.strftime('%Y-%m-%d')
        expiry_dates.append(expiry_date)

    return expiry_dates



















