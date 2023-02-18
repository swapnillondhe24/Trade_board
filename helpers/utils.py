import json
import csv
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import os


def getApi():
    load_dotenv()

    API_KEY_ID = os.getenv('API_KEY_ID')
    SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
    
    api = tradeapi.REST(API_KEY_ID, SECRET_ACCESS_KEY, base_url='https://paper-api.alpaca.markets' ,api_version='v2')
    
    return api



def write_order_to_csv(order, filename):
    headers = ['order_id', 'symbol', 'qty', 'side', 'type', 'time_in_force', 'submitted_at', 'filled_at', 'filled_qty', 'filled_avg_price']
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as order_file:
        writer = csv.DictWriter(order_file, fieldnames=headers)
        
        if not file_exists:
            writer.writeheader()
            
        try:
            writer.writerow({
            'order_id': order['id'],
            'symbol': order['symbol'],
            'qty': order['qty'],
            'side': order['side'],
            'type': order['type'],
            'time_in_force': order['time_in_force'],
            'submitted_at': str(order['submitted_at']),
            'filled_at': str(order['filled_at']) if order['filled_at'] else '',
            'filled_qty': order['filled_qty'] if order['filled_qty'] else 0,
            'filled_avg_price': order['filled_avg_price']
            })
        except:
            writer.writerow({
            'order_id': order.id,
            'symbol': order.symbol,
            'qty': order.qty,
            'side': order.side,
            'type': order.type,
            'time_in_force': order.time_in_force,
            'submitted_at': str(order.submitted_at),
            'filled_at': str(order.filled_at) if order.filled_at else '',
            'filled_qty': order.filled_qty if order.filled_qty else 0,
            'filled_avg_price': order.filled_avg_price
            })
        
        order_file.close()
        
    write_order_details_to_json(filename)


def move_files_to_history(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for file_name in os.listdir(source_dir):
        src_path = os.path.join(source_dir, file_name)
        dest_path = os.path.join(dest_dir, file_name)
        os.rename(src_path, dest_path)




def write_order_details_to_json(filepath):
    api = getApi()
    order_details = []
    with open(filepath, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # skip header row
        for row in csv_reader:
            order_id = row[0]
            order = api.get_order(order_id)
            order_dict = {
                'order ID': order.id,
                'Symbol': order.symbol,
                'Qty': order.qty,
                'filled_qty': order.filled_qty,
                'Type': order.side,
                'side': order.side,
                'time_in_force': order.time_in_force,
                'Status': order.status,
                'Price': order.filled_avg_price,
                'Time': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }
            order_details.append(order_dict)
            
    transactions = {"transaction": order_details}
    
    
            
    with open('../resources/transaction.json', 'w') as outfile:
        json.dump(transactions, outfile)

# write_order_details_to_json("../resources/crossover_strategy")

