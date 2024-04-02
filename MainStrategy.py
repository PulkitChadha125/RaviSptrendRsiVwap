import AliceBlueIntegration, FivePaisaIntegration
import time
import traceback
import pandas as pd
from pathlib import Path
import pyotp
from datetime import datetime, timedelta, timezone

FivePaisaIntegration.login()
AliceBlueIntegration.login()
AliceBlueIntegration.get_nfo_instruments()

def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_zerodha_credentials():
    delete_file_contents("OrderLog.txt")
    credentials = {}
    try:
        df = pd.read_csv('MainSettings.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials

credentials_dict = get_zerodha_credentials()

def custom_round(price, symbol):
    rounded_price = None
    if symbol == "NIFTY":
        last_two_digits = price % 100
        if last_two_digits < 25:
            rounded_price = (price // 100) * 100
        elif last_two_digits < 75:
            rounded_price = (price // 100) * 100 + 50
        else:
            rounded_price = (price // 100 + 1) * 100
            return rounded_price

    elif symbol == "BANKNIFTY":
        last_two_digits = price % 100
        if last_two_digits < 50:
            rounded_price = (price // 100) * 100
        else:
            rounded_price = (price // 100 + 1) * 100
        return rounded_price

    else:
        pass

    return rounded_price


def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')





result_dict = {}


def get_user_settings():
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}

        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'Symbol': row['Symbol'],
                'Timeframe': row['Timeframe'],
                'Quantity': row['Quantity'],
                'OPTION_CONTRACT_TYPE': row['OPTION CONTRACT TYPE'],
                'strike_distance': int(row['strike distance']),
                "RSI_PERIOD": int(row['RSI_PERIOD']),
                "RSI_BUY_VALUE": float(row['RSI_BUY_VALUE']),
                "RSI_SELL_VALUE": float(row['RSI_SELL_VALUE']),
                "RSI_EXIT_BUY": float(row['RSI_EXIT_BUY']),
                "RSI_EXIT_SELL": float(row['RSI_EXIT_SELL']),
                "ATR_PERIOD": int(row['ATR_PERIOD']),
                "SUPERTREND_PERIOD": int(row['SUPERTREND_PERIOD']),
                "SUPERTREND_MULTIPLIER": float(row['SUPERTREND_MULTIPLIER']),
                "runtime": datetime.now(),
                "cool": row['Sync'],
                "rsi1": None,
                "rsi2": None,
                "atr": None,
                "TradeAtr": None,
                "supertrendvalue1": None,
                "supertrendvalue2": None,
                "vwap": None,
                "vwap2": None,
                'close': None,
                'close2': None,
                'low': None,
                'high': None,
                'Trade': None,
                'Breakeven': None,
                'Stoploss': None,
                'ep': None,
                'RsiCondition1': None,
                'RsiCondition2': None,
                "order_token": None,
                "optioncontract": None,
                "producttype": row['PRODUCT_TYPE'],
                "INITIAL_TRADE": None,
                "callstrike": None,
                "putstrike": None,
                "currstrike": None,
                "TradingEnable": True,
                "BUY": False,
                "SHORT": False,
                "candletime":None,
                "token":None,
                "runtoken":False,

            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ", result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_user_settings()


def round_down_to_interval(dt, interval_minutes):
    remainder = dt.minute % interval_minutes
    minutes_to_current_boundary = remainder

    rounded_dt = dt - timedelta(minutes=minutes_to_current_boundary)

    rounded_dt = rounded_dt.replace(second=0, microsecond=0)

    return rounded_dt


def determine_min(minstr):
    min = 0
    if minstr == "1m":
        min = 1
    if minstr == "3m":
        min = 3
    if minstr == "5m":
        min = 5
    if minstr == "15m":
        min = 15
    if minstr == "30m":
        min = 30

    return min
def find_scrip_code( symbol_root, expiry):
    dt_obj = datetime.strptime(expiry, '%d-%m-%Y')
    formatted_date = dt_obj.strftime('%d %b %Y')
    name= symbol_root+ " " + formatted_date
    print(name)
    df= pd.read_csv("ScripMaster.csv")
    for index, row in df.iterrows():
        # print(row['Name'])
        if (row['Name'] == name):
            # Return the ScripCode value if conditions are met
            return row['ScripCode']
        # Return None if no matching row is found
    return None

def main_strategy():
    global result_dict, next_specific_part_time, total_pnl, runningpnl, niftypnl, bankniftypnl
    ExpieryList = []
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                ExpieryList = FivePaisaIntegration.get_active_expiery(symbol=symbol)
                print(ExpieryList)
                today = datetime.now()
                present_month_dates = [date for date in ExpieryList if
                                       datetime.strptime(date, '%Y-%m-%d').month == today.month]

                if present_month_dates:
                    # highest_date = max(present_month_dates)
                    # highest_date = datetime.strptime(highest_date, '%Y-%m-%d')
                    # highest_date = highest_date.strftime('%d-%m-%Y')
                    if  params['Symbol'] == "NIFTY":
                        highest_date = present_month_dates[-1]
                        highest_date = datetime.strptime(highest_date, '%Y-%m-%d')
                        highest_date = highest_date.strftime('%d-%m-%Y')
                    if  params['Symbol'] == "BANKNIFTY":
                        highest_date = present_month_dates[-2]
                        highest_date = datetime.strptime(highest_date, '%Y-%m-%d')
                        highest_date = highest_date.strftime('%d-%m-%Y')
                else:
                    first_day_next_month = today.replace(day=1)
                    first_day_next_month = first_day_next_month.replace(month=first_day_next_month.month + 1)
                    # Filter expiry dates for the next month
                    next_month_dates = [date for date in ExpieryList if
                                        datetime.strptime(date, '%Y-%m-%d').month == first_day_next_month.month]
                    # Get the highest date) from the next month dates
                    print("next_month_dates: ",next_month_dates)
                    highest_date = next_month_dates[-2]
                    highest_date = datetime.strptime(highest_date, '%Y-%m-%d')

                    # Format the highest date as 'DD-MM-YYYY'
                    highest_date = highest_date.strftime('%d-%m-%Y')


                print(f"Symbol: {symbol},highest_date: {highest_date} ")



                present_date = datetime.now().strftime('%Y-%m-%d')

                if ExpieryList[0] == present_date:
                    Expiery = ExpieryList[1]
                else:
                    Expiery = ExpieryList[0]

                # print(f"Symbol= {symbol}, exp={Expiery}")
                if params['Symbol'] == "NIFTY" and params["runtoken"]==False:
                    token=find_scrip_code(symbol_root="NIFTY", expiry=highest_date)
                    print("NIFTY: ",token)
                    params["token"] = token
                    params["runtoken"] = True


                if params['Symbol'] == "BANKNIFTY" and params["runtoken"]==False:
                    token=find_scrip_code(symbol_root="BANKNIFTY", expiry=highest_date)
                    print("BANKNIFTY: ",token)
                    params["token"] = token
                    params["runtoken"] = True


            if datetime.now() >= params["runtime"]:
                try:
                    if params["cool"] == True:
                        time.sleep(int(1))

                    data = FivePaisaIntegration.get_historical_data(timframe=str(params['Timeframe']),
                                                                    token=params["token"],
                                                                    RSIPeriod=params['RSI_PERIOD'],
                                                                    Spperios=params['SUPERTREND_PERIOD'],
                                                                    spmul=params['SUPERTREND_MULTIPLIER'],
                                                                    atrperiod=params['ATR_PERIOD'],
                                                                    symbol=params['Symbol'])
                    # print(f"sym={symbol}, data ={data}")
                    last_two_rows = data.tail(2)
                    print("last_two_rows: ", last_two_rows)
                    second_last_candle = last_two_rows.iloc[-2]
                    last_candle = last_two_rows.iloc[-1]
                    # print(last_two_rows)
                    candletime=last_candle['Datetime']
                    params["candletime"] = candletime
                    rsi1 = last_candle['RSI']
                    rsi2 = second_last_candle['RSI']

                    Supertrend1 = last_candle['Supertrend Signal']
                    Supertrend2 = second_last_candle['Supertrend Signal']

                    VWAP = last_candle['VWAP']
                    VWAP2 = second_last_candle['VWAP']

                    ATR_VALUE = last_candle['ATR_VALUE']
                    close = last_candle['Close']
                    close2 = second_last_candle['Close']
                    low = last_candle['Low']
                    high = last_candle['High']

                    params['rsi1'] = rsi1
                    params['rsi2'] = rsi2
                    params['atr'] = ATR_VALUE
                    params['supertrendvalue1'] = Supertrend1
                    params['supertrendvalue2'] = Supertrend2
                    params['vwap'] = VWAP
                    params["vwap2"] = VWAP2
                    params['close'] = close
                    params['close2'] = close2
                    params['low'] = low
                    params['high'] = high

                    next_specific_part_time = datetime.now() + timedelta(
                        seconds=determine_min(params["Timeframe"]) * 60)
                    next_specific_part_time = round_down_to_interval(next_specific_part_time,
                                                                     determine_min(params["Timeframe"]))
                    print("Next datafetch time = ", next_specific_part_time)
                    params['runtime'] = next_specific_part_time




                except Exception as e:
                    print("Error happened in Main strategy loop: ", str(e))
                    traceback.print_exc()

            ltp = FivePaisaIntegration.get_ltp(params["token"])
            print(
                f"Candletime: {params['candletime'] }, Symbol:{symbol} , ltp:{ltp} ,Rsi1= {params['rsi1']},Rsi2= {params['rsi2']},supertrendvalue1= {params['supertrendvalue1']},"
                f"vwap= {params['vwap']},close={params['close']},params['INITIAL_TRADE']: {params['INITIAL_TRADE']},buy={params['BUY'] },sell={params['SHORT']}"
                f", RsiBuy: {params['RSI_BUY_VALUE']}, Rsisell: {params['RSI_SELL_VALUE']},BuyExit={params['RSI_EXIT_BUY']},SellExit={params['RSI_EXIT_SELL']}")

            if (
                    float(params['rsi2']) < float(params["RSI_BUY_VALUE"]) and
                    float(params['rsi1']) >= float(params["RSI_BUY_VALUE"])  and
                    params['supertrendvalue1']== 1 and
                    float(params['close']) > float(params['vwap']) and
                    params["TradingEnable"]== True and
                    params["BUY"] == False
            ):


                if params['INITIAL_TRADE'] == "SHORT":
                    AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                                 expiry_date=Expiery,
                                                 strike=params["putstrike"], call=True,
                                                 producttype=params["producttype"])
                params['Trade'] = "BUY"
                params["BUY"] = True
                params["SHORT"] = False
                if params["OPTION_CONTRACT_TYPE"] == "ATM":
                    strike = custom_round(int(float(ltp)), symbol)
                    callstrike = strike
                    params["callstrike"] = callstrike

                if params["OPTION_CONTRACT_TYPE"] == "ITM":
                    strike = custom_round(int(float(ltp)), symbol)
                    callstrike = int(strike) - int(params["strike_distance"])
                    params["callstrike"] = callstrike

                if params["OPTION_CONTRACT_TYPE"] == "OTM":
                    strike = custom_round(int(float(ltp)), symbol)
                    callstrike = int(strike) + int(params["strike_distance"])
                    params["callstrike"] = callstrike

                params["putstrike"] = None
                params["currstrike"] = params["callstrike"]
                result = AliceBlueIntegration.option_contract(exch="NFO", symbol=symbol, expiry_date=Expiery,
                                                              strike=params["callstrike"], call=True)
                token_value = result.token
                name_value = result.name
                params["order_token"] = token_value
                params["optioncontract"] = name_value
                params["TradeAtr"] = float(params['atr'])
                params['Breakeven'] = params['close'] + params["TradeAtr"]
                params['Stoploss'] = params['low']
                params['ep'] = ltp
                params['RsiCondition1'] = False
                params['RsiCondition2'] = False
                orderlog = f'{timestamp} Buy order executed @ {symbol} @ {ltp}, option contract= {params["optioncontract"]}, atr value={params["TradeAtr"]}, initial sl={params["Stoploss"]} next TSL Level={params["Breakeven"]}'
                print(orderlog)
                write_to_order_logs(orderlog)
                AliceBlueIntegration.buy(quantity=params["Quantity"], exch="NFO", symbol=symbol, expiry_date=Expiery,
                                         strike=params["callstrike"], call=True, producttype=params["producttype"])

                params["INITIAL_TRADE"] = "BUY"

            if (
                    float(params['rsi2']) > float(params["RSI_SELL_VALUE"]) and
                    float(params['rsi1']) <= float(params["RSI_SELL_VALUE"]) and
                    params['supertrendvalue1'] == -1 and
                    float(params['close']) < float(params['vwap']) and
                    params["TradingEnable"] == True and
                    params["SHORT"] == False
            ):

                if params['INITIAL_TRADE'] == "BUY":
                    AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                                 expiry_date=Expiery,
                                                 strike=params["callstrike"], call=True,
                                                 producttype=params["producttype"])
                if params["OPTION_CONTRACT_TYPE"] == "ATM":
                    strike = custom_round(int(float(ltp)), symbol)
                    putstrike = strike
                    params["putstrike"] = putstrike

                if params["OPTION_CONTRACT_TYPE"] == "ITM":
                    strike = custom_round(int(float(ltp)), symbol)
                    putstrike = int(strike) + int(params["strike_distance"])
                    params["putstrike"] = putstrike

                if params["OPTION_CONTRACT_TYPE"] == "OTM":
                    strike = custom_round(int(float(ltp)), symbol)
                    putstrike = int(strike) - int(params["strike_distance"])
                    params["putstrike"] = putstrike

                params["callstrike"] = None
                params['Trade'] = "SHORT"
                params["BUY"] = False
                params["SHORT"] = True
                params["currstrike"] = params["putstrike"]
                result = AliceBlueIntegration.option_contract(exch="NFO", symbol=symbol, expiry_date=Expiery,
                                                              strike=params["putstrike"], call=False)
                token_value = result.token
                name_value = result.name
                params["order_token"] = token_value
                params["optioncontract"] = name_value
                params["TradeAtr"] = float(params['atr'])
                params['Breakeven'] = params['close'] - params["TradeAtr"]
                params['Stoploss'] = params['high']
                params['ep'] = ltp
                params['RsiCondition1'] = False
                params['RsiCondition2'] = False
                orderlog = f'{timestamp} Sell order executed @ {symbol} @ {ltp}, option contract= {params["optioncontract"]}, atr value={params["TradeAtr"]}, initial sl={params["Stoploss"]} next TSL Level={params["Breakeven"]}'
                print(orderlog)
                write_to_order_logs(orderlog)
                AliceBlueIntegration.buy(quantity=params["Quantity"], exch="NFO", symbol=symbol, expiry_date=Expiery,
                                         strike=params["putstrike"], call=False, producttype=params["producttype"])

                params["INITIAL_TRADE"] = "SHORT"

            #         exit logic coding
            if (
                    params['Trade'] == "BUY" and
                    params['supertrendvalue1'] == -1 and
                    params['supertrendvalue2'] == 1
            ):
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                orderlog = f'{timestamp} Supertrend switch buy order exit @ {symbol} @ {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["callstrike"], call=True, producttype=params["producttype"])

            if (
                    params['Trade'] == "BUY" and
                    float(params['close']) <= float(params['vwap']) and
                    float(params['close2']) > float(params["vwap2"])
            ):
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                orderlog = f'{timestamp} VWAP buy order exit @ {symbol} @ {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["callstrike"], call=True, producttype=params["producttype"])

            if (
                    params['Trade'] == "BUY" and
                    float(ltp) >= float(params['Breakeven']) > 0
            ):
                params['Stoploss'] = params['Stoploss'] + params["TradeAtr"]
                params['Breakeven'] = float(params['close']) + params["TradeAtr"]
                orderlog = f'{timestamp} Tsl point acheived buy trade @ {symbol} stoploss  : {params["Stoploss"]}, ltp: {ltp}, atr value={params["TradeAtr"]}, next TSL Level={params["Breakeven"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if (
                    params['Trade'] == "BUY" and
                    float(ltp) <= float(params['Stoploss'])
            ):
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["callstrike"], call=True, producttype=params["producttype"])
                orderlog = f'{timestamp} Stoploss executed @ buy trade @ {symbol}, ltp = {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if (
                    params['Trade'] == "SHORT" and
                    params['supertrendvalue1'] == 1 and
                    params['supertrendvalue2'] == -1
            ):
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["putstrike"], call=False, producttype=params["producttype"])
                orderlog = f'{timestamp} Supertrend switch sell order exit @ {symbol} @ {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if (
                    params['Trade'] == "SHORT" and
                    float(params['close']) >= float(params['vwap']) and
                    float(params['close2']) < float(params["vwap2"])
            ):
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["putstrike"], call=False, producttype=params["producttype"])
                orderlog = f'{timestamp} VWAP sell order exit @ {symbol} @ {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if (
                    params['Trade'] == "SHORT" and
                    float(ltp) <= float(params['Breakeven']) and
                    float(params['Breakeven']) > 0
            ):
                params['Stoploss'] = params['Stoploss'] - params["TradeAtr"]
                params['Breakeven'] = float(params['close']) - params["TradeAtr"]
                orderlog = f'{timestamp} Tsl point acheived sell trade @ {symbol}  stoploss  : {params["Stoploss"]}, ltp: {ltp}, atr value={params["TradeAtr"]}, next TSL Level={params["Breakeven"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if (
                    params['Trade'] == "SHORT" and
                    float(ltp) >= float(params['Stoploss'])
            ):
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["putstrike"], call=False, producttype=params["producttype"])
                orderlog = f'{timestamp} Stoploss executed @ sell trade @ {symbol}, ltp = {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            #          rsi based exit


            if (
                    params['Trade'] == "BUY" and
                    float(params['rsi2']) >= float(params["RSI_EXIT_BUY"]) and
                    float(params['rsi1']) < float(params["RSI_EXIT_BUY"]) and

                    params['RsiCondition2'] == False
            ):
                params['RsiCondition1'] = True
                params['RsiCondition2'] = True
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["callstrike"], call=False, producttype=params["producttype"])
                orderlog = f'{timestamp} Rsi Exit Buy  @ {symbol}, ltp = {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)



            if (
                    params['Trade'] == "SHORT" and
                    float(params['rsi2']) <= float(params["RSI_EXIT_SELL"]) and float(params['rsi1'])> float(params["RSI_EXIT_SELL"]) and
                    params['RsiCondition2'] == False
            ):
                params['RsiCondition2'] = True
                params['Trade'] = None
                params['INITIAL_TRADE'] = None
                params["BUY"] = False
                params["SHORT"] = False
                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["putstrike"], call=False, producttype=params["producttype"])
                orderlog = f'{timestamp} Rsi Exit sell  @ {symbol}, ltp = {ltp}, option contract= {params["optioncontract"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


def time_based_exit():
    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str) and params["TradingEnable"] == True and params[
                'INITIAL_TRADE'] is not None:
                Expiery = str(params['Expiery'])
                Expiery = datetime.strptime(Expiery, "%d-%m-%Y")
                Expiery = Expiery.strftime("%Y-%m-%d")
                orderlog = f"{timestamp} {params['Symbol']}: Time based exit occured no more trades will be taken "
                print(orderlog)
                write_to_order_logs(orderlog)
                params["TradingEnable"] = False

                AliceBlueIntegration.buyexit(quantity=params["Quantity"], exch="NFO", symbol=symbol,
                                             expiry_date=Expiery,
                                             strike=params["currstrike"], call=False, producttype=params["producttype"])


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()

while True:
    StartTime = credentials_dict.get('StartTime')
    Stoptime = credentials_dict.get('Stoptime')
    start_time = datetime.strptime(StartTime, '%H:%M').time()
    stop_time = datetime.strptime(Stoptime, '%H:%M').time()

    now = datetime.now().time()
    if now >= start_time and now < stop_time:
        main_strategy()
        time.sleep(1)

    if now >= stop_time:
        time_based_exit()
        exit()
