import json
import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
import datetime as dt

pd.options.mode.chained_assignment = None 

try:
    from utils import getApi
except:
    from helpers.utils import getApi

api = getApi()


def realized_profit_df_strategy():
    
    with open('E:/Quanturf/Trade_board/resources/transaction.json') as json_data:
        data = json.load(json_data)
    df = pd.json_normalize(data,record_path=['transaction'])

    result_df = pd.DataFrame(columns = ['Qty','price','symbol','transaction_time','order_id'])
    order_id_list = []
    qty_list = []
    price_list = []
    symbol_list = []
    transaction_time_list = []
    type_list = []

    for index,obj in df.iterrows():
        order_id_list.append(obj["order ID"])
        qty_list.append(obj["Qty"])
        price_list.append(obj["Price"])
        symbol_list.append(obj["Symbol"])
        transaction_time_list.append(obj["Time"])
        type_list.append(obj["Type"])
    
    result_df = pd.DataFrame({
            'order_id':order_id_list,
            'Qty': qty_list, 
            'Price': price_list, 
            'Symbol': symbol_list, 
            'Transaction_time': transaction_time_list, 
            'Type': type_list})
    df_buy = result_df[result_df.Type == 'buy']

    df_sell = result_df[result_df.Type == 'sell']

    df = pd.merge(df_buy, df_sell, on = 'Symbol', how = 'right', suffixes = ['_buy','_sell'])

    df_unrealized = result_df[~result_df['Symbol'].isin(df_sell.Symbol.unique())]
    testing = df_sell.sort_values(by = 'Transaction_time')
    convert_dict = {'Price': float}
    testing = testing.astype(convert_dict)
    df_buy = df_buy.astype(convert_dict)
    output_frame = []

    for sym in testing.Symbol.unique():
        buy = df_buy.loc[df_buy.Symbol == sym] 
        sell = testing.loc[testing.Symbol == sym] 

        obs = [] 
        for i, row in sell.iterrows():
            output_dict = {}
            if i not in obs:
                out = buy.loc[(buy.Transaction_time < row.Transaction_time)]
                idx = [j for j in out.index if j not in obs]
                if idx != []:
                    out = out.loc[idx]
                else:
                    out=out.loc[obs]
                output_dict = {
                                'Symbol': sym, 
                                'selling_qty': float(row.Qty),
                                'Avg_selling_Price': row.Price,
                                'Avg_buying_cost': round(out.groupby('Symbol').Price.mean()[0],2),
                                'Sell_time': row.Transaction_time,
                                'Profit_per_unit': round(row.Price - out.groupby('Symbol').Price.mean()[0],2),
                                'Total Profit': round((row.Price - out.groupby('Symbol').Price.mean())[0] * float(row.Qty),2),
                                'Winning_bet?': True if round(row.Price - out.groupby('Symbol').Price.mean()[0],2) > 0 else False}
                output_frame.append(output_dict)

                if len(idx) > 1:
                    for ix in idx:
                        obs.append(ix)

    output_frame #convert it in json format
    json_output = json.dumps(output_frame,indent=4)
    # print(json_output)
    return output_frame
    

def unrealised_profit_df_strategy():
    with open('E:/Quanturf/Trade_board/resources/transaction.json') as json_data:
        data = json.load(json_data)
    df = pd.json_normalize(data,record_path=['transaction'])

    sell_order_list=[]
    buy_order_list=[]    

    for index,obj in df.iterrows():
        # print(obj)
        if obj.side == "sell":
            sell_order_list.append({
                "Symbol": obj["Symbol"],
                "Qty": obj["Qty"],
                "price": obj["Price"],
                "Time": obj["Time"],
                "Status": obj["Status"],
                "Type": obj["Type"],
                "order ID": obj["order ID"]
            })
        else:
            buy_order_list.append({
                "Symbol": obj["Symbol"],
                "Qty": obj["Qty"],
                "price": obj["Price"],
                "Time": obj["Time"],
                "Status": obj["Status"],
                "Type": obj["Type"],
                "order ID": obj["order ID"]
            })
    for sell_order in reversed(sell_order_list):
        curr_sell_order_symbol = sell_order["Symbol"]
        curr_sell_order_qty = float(sell_order["Qty"])
        curr_sell_order_transaction_time = sell_order["Time"]

        buy_order_index_that_are_closed = []
        for index, buy_order in reversed(list(enumerate(buy_order_list))):
            curr_buy_order_qty = float(buy_order["Qty"])
            if curr_sell_order_qty == 0:
                break
            if buy_order["Symbol"] == curr_sell_order_symbol and buy_order["Time"] < curr_sell_order_transaction_time:
                if curr_buy_order_qty <= curr_sell_order_qty:
                    
                    curr_sell_order_qty = curr_sell_order_qty - curr_buy_order_qty
                    buy_order_index_that_are_closed.append(index)
                elif curr_buy_order_qty > curr_sell_order_qty:
                    buy_order["Qty"] = buy_order["Qty"] - curr_sell_order_qty
                    break
        #update the buy order containing only open position orders
        buy_order_list = [item for idx, item in enumerate(buy_order_list) if idx not in buy_order_index_that_are_closed]
    

    account_positions = api.list_positions()
    current_price_dict = {}
    for position in account_positions:
        current_price_dict[position.symbol] = float(position.current_price)

    output_frame = []
    
    for res in buy_order_list:
        output_dict = {}
        current_price = float(current_price_dict[(res["Symbol"]).replace("/", "")])
        output_dict["Symbol"]=res["Symbol"]
        output_dict["Qty"]=res["Qty"]
        output_dict["Price"]=res["price"]
        output_dict["Transaction Time"]=res["Time"]
        output_dict["Urealized Profit"]=round(current_price-float(res["price"]), 2)
        output_dict["Total Unrealized Profit"]=round(float(res["Qty"])*round(current_price-float(res["price"]), 2),2)
        output_frame.append(output_dict)
        
    transaction_json = json.dumps(output_frame, indent=4)
    return output_frame

def get_pnl_df_strategy(open_positions:list, close_positions:list):
     
    #open
    open_df = pd.DataFrame(columns = ['Qty','price','symbol','transaction_time','unrealized_profit','total_unrealized_profit'])
    qty_list = []
    price_list = []
    symbol_list = []
    transaction_time_list = []
    unrealized_profit_list=[]
    total_unrealized_profit_list=[]

    for obj in open_positions:
        qty_list.append(obj["Qty"])
        price_list.append(obj["Price"])
        symbol_list.append(obj["Symbol"])
        transaction_time_list.append(obj["Transaction Time"])
        unrealized_profit_list.append(obj["Urealized Profit"])
        total_unrealized_profit_list.append(obj["Total Unrealized Profit"])
    
    open_df = pd.DataFrame({
        'Qty':qty_list,
        'price':price_list,
        'symbol':symbol_list,
        'transaction_time':transaction_time_list,
        'unrealized_profit':unrealized_profit_list,
        'total_unrealized_profit':total_unrealized_profit_list,
    })
    open_df['price'] = open_df['price'].astype(float)
    open_df['Qty'] = open_df['Qty'].astype(float)
    
    open_df['date'] =  pd.to_datetime(open_df['transaction_time'], errors='coerce')
    unrealized_pnl_df = open_df.groupby('date')['total_unrealized_profit'].sum().reset_index()
    
    #close
    close_df=pd.DataFrame(columns=['Sybmol','selling_qty','Avg_selling_Price','Avg_buying_cost','Avg_holding_period_days','Sell_time','Profit_per_unit','Total Profit'])
    
    symbol_list=[]
    selling_qty_list=[]
    Avg_selling_Price_list=[]
    Avg_buying_cost_list=[]
    Sell_time_list=[]
    Profit_per_unit_list=[]
    Total_Profit_list=[]
    winning_list=[]

    for obj in close_positions:
        symbol_list.append(obj['Symbol'])
        selling_qty_list.append(obj['selling_qty'])
        Avg_selling_Price_list.append(obj['Avg_selling_Price'])
        Avg_buying_cost_list.append(obj['Avg_buying_cost'])
        Sell_time_list.append(obj['Sell_time'])
        Profit_per_unit_list.append(obj['Profit_per_unit'])
        Total_Profit_list.append(obj['Total Profit'])
        winning_list.append(obj['Winning_bet?'])
    
    close_df=pd.DataFrame({
        'Symbol':symbol_list,
        'selling_qty':selling_qty_list,
        'Avg_selling_Price':Avg_selling_Price_list,
        'Avg_buying_cost':Avg_buying_cost_list,
        'Sell_time':Sell_time_list,
        'Profit_per_unit':Profit_per_unit_list,
        'Total Profit':Total_Profit_list,
        'winning_bet':winning_list
    })
    close_df['Avg_buying_cost'] = close_df['Avg_buying_cost'].astype('float')
    close_df['date'] = pd.to_datetime(close_df['Sell_time'], errors='coerce')
    realized_pnl_df = close_df.groupby('date')['Total Profit'].sum().reset_index()

    df = pd.merge(unrealized_pnl_df, realized_pnl_df, on='date', how='outer')
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.rename(columns={'Total Profit': 'realized_pnl', 'total_unrealized_profit': 'unrealized_pnl'})
    df = df.fillna(0)
    df['total_pnl'] = df['realized_pnl'] + df['unrealized_pnl']
    
    Total_Profit = df['realized_pnl'].sum() + df['unrealized_pnl'].sum()
    
    # print(round(close_df['Avg_buying_cost'].sum()*close_df['selling_qty'].sum(),2))
    # print(round(open_df['price'].sum()*open_df['Qty'].sum(),2))
    # initial_investment = close_df['Avg_buying_cost'].sum() + open_df['price'].sum()
    initial_investment = round(close_df['Avg_buying_cost'].sum()*close_df['selling_qty'].sum() + open_df['price'].sum()*open_df['Qty'].sum(),4)
    
    return_percentage = round((Total_Profit/initial_investment)*100, 4)
    
    win_rate = (close_df['winning_bet'].sum()/close_df['winning_bet'].count())*100
    
    
    result_dict = {
        'transaction': df.to_dict('records'),
        'total_profit_all_trades': Total_Profit,
        'total_realized_profit': df['realized_pnl'].sum(),
        'total_unrealized_profit': df['unrealized_pnl'].sum(),
        'return_percentage': return_percentage,
        'total_capital_invested': initial_investment,
        'available_capital': api.get_account().cash,
        'win_rate': win_rate,
        
    }
    
    return json.dumps(result_dict, indent=4)


if __name__ =="__main__":
    # rp = realized_profit_df_strategy()
    # print(rp)
    # up = unrealised_profit_df_strategy()
    # print(up)
    js = get_pnl_df_strategy(unrealised_profit_df_strategy(),realized_profit_df_strategy())
    print(js)
