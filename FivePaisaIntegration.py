AppName="5P50101877"
AppSource=21885
UserID="B8I7uoAKrTv"
Password="v20Crs1503k"
UserKey="BqlWZe4zncP6S2WKTHRDw7yUz8L7tCZP"
EncryptionKey="ZAsxzvvnWK6sj3qxkfsUBYYhievD0Jbq"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYDCMBRHA3TOXZVKBDUWRKZ"
import pandas_ta as ta
from py5paisa import FivePaisaClient
import pyotp,datetime
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
    client.get_totp_session(client_code=50101877,totp=twofa,pin=654321)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())
def get_historical_data(timframe, token, RSIPeriod, Spperios, spmul, atrperiod):
    global client
    from_time = datetime.datetime.now() - datetime.timedelta(days=5)
    to_time = datetime.datetime.now()
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
    df["ATR_VALUE"] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'],length=atrperiod)
    df.reset_index(inplace=True)
    df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv('check.csv', index=False)

    return df.tail(3)


#
# def get_historical_data(timframe,token,RSIPeriod,Spperios,spmul,atrperiod):
#     global client
#     from_time=datetime.datetime.now()-datetime.timedelta(days=4)
#     to_time=datetime.datetime.now()
#
#     df=client.historical_data('N','D',token,timframe,from_time,to_time)
#     df["RSI"] = ta.rsi(close=df["Close"], length=RSIPeriod)
#     df["VWAP"] = ta.vwap(high=df["High"], low=df["Low"], close=df["Close"],
#                                  volume=df["Volume"])
#     colname = f'SUPERT_{int(Spperios)}_{spmul}'
#     colname2 = f'SUPERTd_{int(Spperios)}_{spmul}'
#
#     df["Supertrend Values"] = ta.supertrend(high=df['inth'], low=df['intl'], close=df['intc'], length=Spperios,
#                                             multiplier=spmul)[colname]
#     df["Supertrend Signal"] = ta.supertrend(high=df['inth'], low=df['intl'], close=df['intc'], length=Spperios,
#                                             multiplier=spmul)[colname2]
#
#     df['Datetime'] = pd.to_datetime(df['Datetime'])
#
#     # Format 'Datetime' column as human-readable
#     df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
#     print(df)
#

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


def get_ltp(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
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





















