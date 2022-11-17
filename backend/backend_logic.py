from datetime import datetime
from dataclasses import dataclass
import datetime

buy = 1
sell = 0


@dataclass(frozen=True)
class Transaction:
    id: int
    name: str
    symbol: str
    Type: str
    value_usd: float
    purchased_price: float
    date: datetime
    coins: float



def convert_entry_to_transaction(entry):
    return {
        "id": entry[0],
        "name": entry[1],
        "symbol": entry[2],
        "Type": entry[3],
        "value_usd": entry[4]/100,
        "purchased_price": float(entry[5]),
        "date": entry[6].strftime("%Y-%m-%d-%H:%M"),
        "coins": float(entry[7])
    }

    