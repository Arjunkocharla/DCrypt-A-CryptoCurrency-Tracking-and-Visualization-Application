get_transactions = f"SELECT * FROM transactions where status!='delete'"
get_detail_coinwise = f"SELECT  symbol,type, SUM(value_usd)/100 as total_value,SUM(coins) as total_coins FROM transactions where status!='delete' GROUP BY symbol, type"



