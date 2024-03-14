from pya3 import *
from datetime import datetime,timedelta
import pandas as pd

userid="172259"
apikey="IVgjUq7lNhM3hCBr0D8Q9jv4hbjrajav5vhQBvOUm1YpjjmSaBan1WCZbtTK0gH0Ll6P80UNhY7E5YfoX2Pl7ZNDj6AArGh8bLAEBWkTBcRyVf1xc8ftgH1R7AapoEmC"
alice=None

def login():
    global alice,userid,apikey
    alice = Aliceblue(user_id=userid,api_key=apikey)
    print(alice.get_session_id())

def get_nfo_instruments():
    global alice
    alice.get_contract_master("NFO")

def get_instrument_detail(exch,symbol,expiry_date):
    global alice
    responce=alice.get_instrument_for_fno(exch=exch, symbol=symbol, expiry_date=expiry_date, is_fut=True, strike=None,
                                     is_CE=False)
    # print(responce)
    token_value = responce.token
    print(token_value)
    return token_value
    # CASH
    # print(alice.get_instrument_by_symbol('INDICES','NIFTY BANK'))
    # print(alice.get_instrument_by_symbol('INDICES', 'NIFTY 50'))

def get_ltp(token):
    global alice
    responce =alice.get_scrip_info(alice.get_instrument_by_token("NFO",token))
    print(responce)


def option_contract(exch,symbol,expiry_date,strike,call):
    global alice

    res= alice.get_instrument_for_fno(exch=exch, symbol=symbol, expiry_date=expiry_date, is_fut=False, strike=strike,
                                     is_CE=call)
    print("res: ",res)
    return res

def chek():
    return alice.get_instrument_by_symbol('NSE', 'INFY')


def buy(quantity,exch,symbol, expiry_date, strike, call,producttype):
    global alice

    if producttype=="D":
        PT=ProductType.Delivery
    else:
        PT = ProductType.Intraday

    res = alice.place_order(transaction_type=TransactionType.Buy,
                      instrument=option_contract(exch,symbol,expiry_date,strike,call),
                      quantity=quantity,
                      order_type=OrderType.Market,
                      product_type=PT,
                      price=0.0,
                      trigger_price=None,
                      stop_loss=None,
                      square_off=None,
                      trailing_sl=None,
                      is_amo=False,
                      order_tag='Programetix Automation')

    print("Buy order res: ",res)

def buyexit(quantity,exch,symbol, expiry_date, strike, call,producttype):
    global alice
    if producttype=="D":
        PT=ProductType.Delivery
    else:
        PT = ProductType.Intraday
    res = alice.place_order(transaction_type=TransactionType.Sell,
                            instrument=option_contract(exch, symbol, expiry_date, strike, call),
                            quantity=quantity,
                            order_type=OrderType.Market,
                            product_type=PT,
                            price=0.0,
                            trigger_price=None,
                            stop_loss=None,
                            square_off=None,
                            trailing_sl=None,
                            is_amo=False,
                            order_tag='Programetix Automation')

    print("BuyExit order res: ", res)





























def get_historical(token):
    global alice
    instrument = alice.get_instrument_by_token("NFO",token)
    from_datetime = datetime.now() - timedelta(days=1)  # From last & days
    to_datetime = datetime.now()  + timedelta(days=1) # To now
    print("from_datetime:",from_datetime)
    print("to_datetime:", to_datetime)
    interval = "D"  # ["1", "D"]
    indices = False  # For Getting index data
    historical_data = alice.get_historical(instrument, from_datetime, to_datetime, interval, indices)
    df = pd.DataFrame(historical_data)
    df.to_csv("Check.csv")
    return df

