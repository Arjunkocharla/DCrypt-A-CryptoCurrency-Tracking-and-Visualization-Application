import json
from collections import defaultdict
from datetime import datetime

import requests
from backend_logic import buy, convert_entry_to_transaction, sell
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from psycopg2 import pool

price_url = "https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd"

postgreSQL_pool = pool.SimpleConnectionPool(
    1,20,database="cryptodb", user="docker", password="docker", host="127.0.0.1"
)

app = Flask(__name__)
cors = CORS(app)

app.config['postgreSQL_pool'] = postgreSQL_pool

@app.route("/")
def health_check():
    return "DataBase is up and running!!"

@app.route("/transactions", methods=["GET"])
@cross_origin()
def get_transaction():
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM transactions where status!='delete'")
    entry = cur.fetchall()

    transactions = defaultdict(list)
    for entry in entry:
        transactions[entry[1]].append(convert_entry_to_transaction(entry))

    return jsonify(transactions)

@app.route("/get_details_coinwise")
def get_details_coinwise():
    collection = defaultdict(
        lambda:{
        "coins": 0, "total_value": 0, "total_equity": 0, "live_price": 0
}
    )
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()
    cur.execute(f"SELECT  symbol,type, SUM(value_usd)/100 as total_value,SUM(coins) as total_coins FROM transactions where status!='delete' GROUP BY symbol, type")
    entry = cur.fetchall()
    for entry in entry:
        coin = entry[0]
        transaction_type = entry[1]
        transaction_value = entry[2]
        transaction_coins = entry[3]

        if transaction_type == "buy":
            collection[coin]["coins"] += transaction_coins
            collection[coin]["total_value"] += transaction_value

        elif transaction_type == "sell":
            if transaction_coins>=collection[coin]["coins"]:
                collection[coin]["coins"] -= transaction_coins
                collection[coin]["total_value"] -= transaction_value
        

    symbol_coin_mapping = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "XRP": "ripple",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "EOS": "eos",
        "XLM": "stellar",
        "ADA": "cardano",
        "SOL": "solana"

    }

    get_response = {}

    for symbol in collection:
        response = requests.get(f"{price_url}&ids={symbol_coin_mapping[symbol]}").json()
        live_price = response[symbol_coin_mapping[symbol]]["usd"]

        collection[symbol]["live_price"] = live_price
        
        collection[symbol]["total_equity"] = float(collection[symbol]["coins"]) * live_price

        get_response.update({symbol: {
            "symbol": symbol,
            "coins": collection[symbol]["coins"],
            "total_value": collection[symbol]["total_value"],
            "total_equity": collection[symbol]["total_equity"],
            
            "live_price": live_price
        }})
    
        return jsonify(get_response)


def total_coins_value(symbol):

    coin_dict = {"coins": 0, "total_value": 0}
    
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()
    cur.execute(f"SELECT  type, SUM(value_usd) as total_value,SUM(coins) as total_coins FROM transactions where status!='delete' and symbol='{symbol}' GROUP BY symbol, type")
    entry = cur.fetchall()
    for entry in entry:
        
        transaction_type = entry[0]
        transaction_value = entry[1]
        transaction_coins = entry[2]

        if transaction_type == "buy":
            coin_dict["coins"] += transaction_coins
            coin_dict["total_value"] += transaction_value

        elif transaction_type == "sell":
            if transaction_coins>=coin_dict["coins"]:
                coin_dict["coins"] -= transaction_coins
                coin_dict["total_value"] -= transaction_value
    return coin_dict

    
@app.route("/transactions", methods=["POST"])
def add_transaction():
    name = request.json["name"]
    symbol = request.json["symbol"]
    
    type = request.json["type"]
    value_usd = float(request.json["value_usd"])
    purchased_price = float(request.json["purchased_price"])
    date = datetime.strptime(request.json["date"], "%Y-%m-%d-%H:%M")
    coins = float(request.json["coins"])
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()

 #   cur.execute(f"SELECT SUM(value_usd) as total_value,SUM(coins) as total_coins FROM transactions where status!='delete' and symbol = '{symbol}' and type='buy'")

  #  entry = cur.fetchall()
 #   dict_entry = {}

  #  for entry in entry:
   #     dict_entry["total_value"] = entry[0]
    #    dict_entry["total_coins"] = entry[1]
    coin_details = total_coins_value(symbol)

#   cur.execute(f"SELECT SUM(value_usd),SUM(coins) FROM transactions WHERE symbol = '{symbol}' and status!='delete' and type='buy' group by symbol")
 #   entry = cur.fetchall()
    
    if type == "sell":
    #    for entry in entry:
        if coin_details["coins"]>=coins and coin_details["total_value"]>=value_usd:
            cur.execute(f"INSERT INTO transactions (name,symbol,type,value_usd,purchased_price,date,coins,status) VALUES ('{name}','{symbol}','{type}',{value_usd},{purchased_price},'{date}',{coins},'active')")
            conn.commit()
            return jsonify(request.json)
  #  if entry[0] >= value_usd and entry[1] >= coins:
        
           #     add_transaction = f"INSERT INTO transactions (name, symbol,type, value_usd, purchased_price, date, coins) VALUES ('{name}', '{symbol}' , '{type}', {value_usd}, {purchased_price}, '{date}', {coins}) RETURNING *"
          #      cur.execute(add_transaction)
         #       update_total_transactions = f"Update total_transaction_details set (total_value, total_coins) = (select SUM(value_usd),SUM(coins) FROM transactions where status!='delete' and type='buy' and symbol='{symbol}' GROUP BY symbol) where symbol = '{symbol}'"
         #       cur.execute(update_total_transactions)
         #       conn.commit()
    
                #conn.commit()
            #return jsonify(request.json)
        else:
        
        
        
        
             return "You cannot sell more than you have"

    elif type=="buy":
        add_transaction = f"INSERT INTO transactions (name, symbol,type, value_usd, purchased_price, date, coins) VALUES ('{name}', '{symbol}' , '{type}', {value_usd}, {purchased_price}, '{date}', {coins}) RETURNING *"
        cur.execute(add_transaction)
    
        conn.commit()
       
    #    update_total_transactions = f"Update total_transaction_details set (symbol, total_value, total_coins) = (select symbol, SUM(value_usd),SUM(coins) FROM transactions where status!='delete' and type='buy' and symbol='{symbol}' GROUP BY symbol) where symbol = '{symbol}'"
   #     cur.execute(update_total_transactions)
    #    conn.commit()

        return jsonify(request.json)
        
                
    else:
        return "Invalid transaction type, please enter buy or sell"

@app.route("/transactions", methods=["DELETE"])
def delete_transaction():
    id = request.json["id"]
 #   symbol = request.json["symbol"]
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()
    delete_transaction = f"Update transactions set status='delete' where id={id}"
    cur.execute(delete_transaction)
    update_seq = f"ALTER SEQUENCE transactions_id_seq RESTART;"
    cur.execute(update_seq)
    reset_seq = f"UPDATE transactions SET id = DEFAULT;"
    cur.execute(reset_seq)
 #   update_total_transactions = f"Update total_transaction_details set (symbol, total_value, total_coins) = (select symbol, SUM(value_usd),SUM(coins) FROM transactions where status!='delete' and type='buy' GROUP BY symbol) where symbol = '{symbol}'"
  #  cur.execute(update_total_transactions)
    conn.commit()
    return jsonify(request.json)

app.run(debug=True, port=5000)





