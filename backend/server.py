import json
from collections import defaultdict
from datetime import datetime

import requests
from backend_logic import buy, convert_entry_to_transaction, sell
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from psycopg2 import pool
# from sql_commands import get_transactions, get_detail_coinwise;


price_url = "https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd"

postgreSQL_pool = pool.SimpleConnectionPool(
    1,300,database="cryptodb", user="docker", password="docker", host="127.0.0.1"
)

app = Flask(__name__)
cors = CORS(app)

app.config['postgreSQL_pool'] = postgreSQL_pool

@app.route("/")
def health_check():
    return "DataBase is up and running!!"

@app.route("/transactions")

@cross_origin()

def get_transaction():
    
    cur = postgreSQL_pool.getconn().cursor()

    cur.execute(f"select * from transactions where status!='delete' order by date desc limit 15")
    
    entry = cur.fetchall()
    cur.close()
    

    transactions = defaultdict(list)
    for item in entry:
        transactions[item[1]].append(convert_entry_to_transaction(item))

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

    get_response =  []  
    for symbol in collection:
        response = requests.get(f"{price_url}&ids={symbol_coin_mapping[symbol]}").json()
        live_price = response[symbol_coin_mapping[symbol]]["usd"]

        collection[symbol]["live_price"] = live_price
        
        collection[symbol]["total_equity"] = float(collection[symbol]["coins"]) * live_price

        get_response.append({symbol: {
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
    conn.close()       
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
    
    coin_details = total_coins_value(symbol)
    if type == "sell":
        if coin_details["total_value"]>=value_usd:
            cur.execute(f"INSERT INTO transactions (name,symbol,type,value_usd,purchased_price,date,coins) VALUES ('{name}','{symbol}','{type}',{value_usd},{purchased_price},'{date}',{coins})")
            conn.commit()
            return jsonify(request.json)

        else:
            return "You cannot sell more than you have"

    elif type=="buy":
        add_transaction = f"INSERT INTO transactions (name, symbol,type, value_usd, purchased_price, date, coins) VALUES ('{name}', '{symbol}' , '{type}', {value_usd}, {purchased_price}, '{date}', {coins}) RETURNING *"
        cur.execute(add_transaction)
    
        conn.commit()
        conn.close()
        return jsonify(request.json)
        
        
    else:
        conn.close()
        return "Invalid transaction type, please enter buy or sell"

@app.route("/transactions", methods=["DELETE"])
def delete_transaction():
    id = request.json["id"]
    conn = postgreSQL_pool.getconn()
    cur = conn.cursor()
    delete_transaction = f"Update transactions set status='delete' where id={id}"
    cur.execute(delete_transaction)
    update_seq = f"ALTER SEQUENCE transactions_id_seq RESTART;"
    cur.execute(update_seq)
    reset_seq = f"UPDATE transactions SET id = DEFAULT;"
    cur.execute(reset_seq)
    conn.commit()
    conn.close()
    return jsonify(request.json)

app.run(debug=True, port=5000)