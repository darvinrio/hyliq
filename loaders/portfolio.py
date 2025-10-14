from hyperliquid.info import Info
from hyperliquid.utils import constants
from loguru import logger
import polars as pl
import os
import json
from config import cache_dir
from models.portfolio import portfolio_period_enum


def get_portfolio_json(address: str, use_cache: bool = True) -> dict:
    """
    JSON contains periods:
        - perpAllTime
        - perpMonth
        - perpDay
        - week
        - perpWeek
        - allTime
        - month
        - day
    """

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

    df_exploded = pl.DataFrame(rows).cast(
        {
            "timestamp": pl.Datetime("ms"),
            "period": portfolio_period_enum,
        }
    )
    # logger.debug(f"Portfolio DataFrame:\n{df_exploded.tail()}")
    return df_exploded


def combine_portfolios(portfolios: list[pl.DataFrame]) -> pl.DataFrame:
    """
    Combine multiple portfolio DataFrames by summing account_value and pnl for each timestamp.
    When a timestamp is not available for a portfolio, it uses the previous value (forward fill).

    Args:
        portfolios: List of portfolio DataFrames from different addresses

    Returns:
        Combined DataFrame with summed account_value and pnl per timestamp
    """
    if not portfolios:
        return pl.DataFrame()

    if len(portfolios) == 1:
        return portfolios[0]

    # Add portfolio identifier to each DataFrame
    numbered_portfolios = [
        df.with_columns(pl.lit(i).alias("portfolio_id"))
        for i, df in enumerate(portfolios)
    ]

    # Concatenate all portfolios
    all_data = pl.concat(numbered_portfolios)

    # Get all unique timestamp-period combinations
    unique_timestamps = all_data.select(["period", "timestamp"]).unique()

    # For each portfolio, create a complete timeline and forward fill
    filled_portfolios = []
    for i in range(len(portfolios)):
        portfolio_data = all_data.filter(pl.col("portfolio_id") == i)

        # Join with complete timeline to get missing timestamps
        complete_timeline = unique_timestamps.join(
            portfolio_data, on=["period", "timestamp"], how="left"
        ).sort(["period", "timestamp"])

        # Forward fill within each period group
        filled = complete_timeline.with_columns(
            [
                pl.col("account_value").forward_fill().over("period"),
                pl.col("pnl").forward_fill().over("period"),
                pl.col("vlm").forward_fill().over("period"),
                pl.lit(i).alias("portfolio_id"),
            ]
        )

        filled_portfolios.append(filled)

    # Concatenate all filled portfolios and sum by timestamp and period
    result = (
        pl.concat(filled_portfolios)
        .group_by(["period", "timestamp"])
        .agg([pl.col("account_value").sum(), pl.col("pnl").sum(), pl.col("vlm").sum()])
        .sort(["period", "timestamp"])
    )

    return result
