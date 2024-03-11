import AliceBlueIntegration,FivePaisaIntegration
import time
import traceback
import pandas as pd
from pathlib import Path
import pyotp
from datetime import datetime, timedelta, timezone

FivePaisaIntegration.login()

AliceBlueIntegration.login()
AliceBlueIntegration.get_nfo_instruments()
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


result_dict={}
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
                'Quantity':row['Quantity'],
                'Expiery': row['TradeExpiery'],
                'Expiery Type':row['Expiery Type'],
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
                "rsi1":None,
                "rsi2":None,
                "atr":None,
                "supertrendvalue1":None,
                "supertrendvalue2":None,
                "vwap":None,
                "vwap2": None,
                'close':None,
                'close2':None,
                'low':None,
                'high':None,
                'Trade':None,
                'Breakeven': None,
                'Stoploss':None,
                'ep':None,
                'RsiCondition1': None,
                'RsiCondition2': None,


            }
            result_dict[row['Symbol']] = symbol_dict
        print("result_dict: ",result_dict)
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
    min=0
    if minstr =="1m":
        min=1
    if minstr =="5m":
        min=5
    if minstr =="15m":
        min=15
    if minstr =="30m":
        min=30

    return min


def main_strategy ():
    global result_dict,next_specific_part_time,total_pnl,runningpnl,niftypnl,bankniftypnl

    try:
        for symbol, params in result_dict.items():
            symbol_value = params['Symbol']
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            if isinstance(symbol_value, str):
                Expiery = str(params['Expiery'])
                if params['Symbol'] == "NIFTY":
                    token = 36612
                    # usedltp = niftyltp
                if params['Symbol'] == "BANKNIFTY":
                    token = 36611
                    # usedltp = banknifty_ltp
            if datetime.now() >= params["runtime"]:
                try:
                    if params["cool"] == True:
                        time.sleep(int(2))

                    data =FivePaisaIntegration.get_historical_data(timframe=str(params['Timeframe']),
                                                                   token=token,
                                                                   RSIPeriod=params['RSI_PERIOD'],
                                                                   Spperios=params['SUPERTREND_PERIOD'],
                                                                   spmul=params['SUPERTREND_MULTIPLIER'],
                                                                   atrperiod=params['ATR_PERIOD'] )
                    last_two_rows = data.tail(2)
                    second_last_candle = last_two_rows.iloc[-2]
                    last_candle = last_two_rows.iloc[-1]

                    rsi1=last_candle['RSI']
                    rsi2=second_last_candle['RSI']

                    Supertrend1= last_candle['Supertrend Signal']
                    Supertrend2= second_last_candle['Supertrend Signal']

                    VWAP = last_candle['VWAP']
                    VWAP2= second_last_candle['VWAP']

                    ATR_VALUE = last_candle['ATR_VALUE']
                    close=last_candle['Close']
                    close2=second_last_candle['Close']
                    low=last_candle['Low']
                    high=last_candle['High']

                    params['rsi1']=rsi1
                    params['rsi2']=rsi2
                    params['atr']=ATR_VALUE
                    params['supertrendvalue1']=Supertrend1
                    params['supertrendvalue2'] = Supertrend2
                    params['vwap'] =VWAP
                    params["vwap2"] = VWAP2
                    params['close'] =close
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

            ltp=FivePaisaIntegration.get_ltp(token)

            if params['rsi2']<=params["RSI_BUY_VALUE"] and params['rsi1']>params["RSI_BUY_VALUE"] and params['supertrendvalue1']== 1 and \
                params['close'] > params['vwap']:
                params['Trade']="BUY"
                if params["OPTION_CONTRACT_TYPE"] == "ATM":
                    strike = custom_round(int(float(ltp)), symbol)
                    callstrike = strike

                if params["OPTION_CONTRACT_TYPE"] == "ITM":
                    strike = custom_round(int(float(ltp)), symbol)
                    callstrike = int(strike) - int(params["strike_distance"])

                if params["OPTION_CONTRACT_TYPE"] == "OTM":
                    strike = custom_round(int(float(ltp)), symbol)
                    callstrike = int(strike) + int(params["strike_distance"])

                params['Breakeven'] = ltp + params['atr']
                params['Stoploss'] = params['low']
                params['ep']= ltp
                params['RsiCondition1'] = False
                params['RsiCondition2'] = False
                orderlog =f'{timestamp} Buy order executed @ {symbol} @ {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['rsi2']>=params["RSI_SELL_VALUE"] and params['rsi1']<params["RSI_SELL_VALUE"] and params['supertrendvalue1']== -1 and \
                params['close'] < params['vwap']:
                params['Trade']="SHORT"
                if params["OPTION_CONTRACT_TYPE"] == "ATM":
                    strike = custom_round(int(float(ltp)), symbol)
                    putstrike = strike


                if params["OPTION_CONTRACT_TYPE"] == "ITM":
                    strike = custom_round(int(float(ltp)),symbol)
                    putstrike = int(strike) + int(params["strike_distance"])


                if params["OPTION_CONTRACT_TYPE"] == "OTM":
                    strike = custom_round(int(float(ltp)),symbol)
                    putstrike = int(strike) - int(params["strike_distance"])

                params['Breakeven'] = ltp - params['atr']
                params['Stoploss'] = params['high']
                params['ep'] = ltp
                params['RsiCondition1'] = False
                params['RsiCondition2'] = False
                orderlog = f'{timestamp} Sell order executed @ {symbol} @ {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

    #         exit logic coding
            if params['Trade']=="BUY" and params['supertrendvalue1']== -1 and params['supertrendvalue2']== 1 :
                params['Trade']=None
                orderlog = f'{timestamp} Supertrend switch buy order exit @ {symbol} @ {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade']=="BUY" and params['close']< params['vwap']  and params['close2'] > params["vwap2"]== 1 :
                params['Trade']=None
                orderlog = f'{timestamp} Supertrend switch buy order exit @ {symbol} @ {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade'] == "BUY" and params['close'] >= params['Breakeven'] and params['Breakeven']>0:
                params['Stoploss']=params['ep']
                orderlog = f'{timestamp} Tsl point acheived buy trade @ {symbol} stoploss moved to cost to cost : {params["Stoploss"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade'] == "BUY" and params['close'] <= params['Stoploss'] :
                params['Trade'] = None
                orderlog = f'{timestamp} Stoploss executed @ buy trade @ {symbol}, ltp = {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)



            if params['Trade']=="SHORT" and params['supertrendvalue1']== 1 and params['supertrendvalue2']== -1 :
                params['Trade']=None
                orderlog = f'{timestamp} Supertrend switch sell order exit @ {symbol} @ {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade']=="SHORT" and params['close']> params['vwap']  and params['close2'] < params["vwap2"]== 1 :
                params['Trade']=None
                orderlog = f'{timestamp} Supertrend switch sell order exit @ {symbol} @ {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade'] == "SHORT" and params['close'] <= params['Breakeven'] and params['Breakeven']>0:
                params['Stoploss']=params['ep']
                orderlog = f'{timestamp} Tsl point acheived sell trade @ {symbol} stoploss moved to cost to cost : {params["Stoploss"]}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade'] == "SHORT" and params['close'] >= params['Stoploss'] :
                params['Trade'] = None
                orderlog = f'{timestamp} Stoploss executed @ sell trade @ {symbol}, ltp = {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

    #          rsi based exit
            if params['Trade'] == "BUY" and params['rsi2']<=params["RSI_EXIT_BUY"] and params['rsi1']>params["RSI_EXIT_BUY"] and params['RsiCondition1'] == False:
                params['RsiCondition1'] = True

            if params['Trade'] == "BUY" and params['rsi2']<=params["RSI_EXIT_BUY"] and params['rsi1']>params["RSI_EXIT_BUY"] and params['RsiCondition1'] == True and params['RsiCondition2'] == False:
                params['RsiCondition1'] = True
                params['RsiCondition2']= True
                params['Trade'] = None
                orderlog = f'{timestamp} Rsi Exit Buy  @ {symbol}, ltp = {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

            if params['Trade'] == "SHORT" and params['rsi2']>=params["RSI_EXIT_SELL"] and params['rsi1']<params["RSI_EXIT_SELL"] and params['RsiCondition1'] == False:
                params['RsiCondition1'] = True

            if params['Trade'] == "SHORT" and params['rsi2']<=params["RSI_EXIT_SELL"] and params['rsi1']>params["RSI_EXIT_SELL"] and params['RsiCondition1'] == True and params['RsiCondition2'] == False:
                params['RsiCondition1'] = True
                params['RsiCondition2']= True
                params['Trade'] = None
                orderlog = f'{timestamp} Rsi Exit sell  @ {symbol}, ltp = {ltp}'
                print(orderlog)
                write_to_order_logs(orderlog)

    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


while True:
    main_strategy ()



# AliceBlueIntegration.get_instrument_detail(exch="NFO",symbol='BANKNIFTY',expiry_date="2024-03-27")
# AliceBlueIntegration.get_instrument_detail(exch="NFO",symbol='NIFTY',expiry_date="2024-03-28")
# AliceBlueIntegration.get_ltp(token=36612)
#
#
