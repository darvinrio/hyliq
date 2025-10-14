from hyperliquid.info import Info
from hyperliquid.utils import constants
import polars as pl
import os
import json
from config import cache_dir


def get_portfolio_json(address: str, use_cache: bool = True) -> dict:

    portfolio_dir = os.path.join(cache_dir, "portfolio")
    os.makedirs(portfolio_dir, exist_ok=True)
    cache_path = os.path.join(portfolio_dir, f"{address.lower()}.json")

    if os.path.isfile(cache_path) and use_cache:
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        info = Info(constants.MAINNET_API_URL, skip_ws=True)
        user_state = info.portfolio(address.lower())

        with open(cache_path, "w") as f:
            json.dump(user_state, f, indent=4)

    return user_state


def get_portfolio(address: str, use_cache: bool = True) -> pl.DataFrame:
    rows = []
    user_state = get_portfolio_json(address, use_cache)
    for item in user_state:
        period = item[0]
        vlm = item[1]["vlm"]

        # Combine accountValueHistory and pnlHistory by timestamp
        for acct_record, pnl_record in zip(
            item[1]["accountValueHistory"], item[1]["pnlHistory"]
        ):
            rows.append(
                {
                    "period": period,
                    "timestamp": int(acct_record[0]),
                    "account_value": float(acct_record[1]),
                    "pnl": float(pnl_record[1]),
                    "vlm": float(vlm),
                }
            )

    df_exploded = pl.DataFrame(rows)
    print(df_exploded)
