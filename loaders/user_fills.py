import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.df_models.user_fills import user_fills_schema


def get_user_fills_json(
    address: str, use_cache: bool = True, aggregate_by_time: bool = True
) -> list:
    """
    Fetch user fills from the Hyperliquid API.

    Args:
        address: User address to fetch fills for
        use_cache: Whether to use cached data if available
        aggregate_by_time: Whether to aggregate fills by time (matches API parameter)

    Returns:
        List containing user fills data from the API
    """

    user_fills_dir = os.path.join(cache_dir, "user_fills")
    os.makedirs(user_fills_dir, exist_ok=True)

    # Include aggregation setting in cache filename
    agg_suffix = "_agg" if aggregate_by_time else "_no_agg"
    cache_path = os.path.join(
        user_fills_dir, f"{address.lower()}_user_fills{agg_suffix}.json"
    )

    if os.path.isfile(cache_path) and use_cache:
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        # Make API request to Hyperliquid API
        url = "https://api-ui.hyperliquid.xyz/info"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
        }
        payload = {
            "aggregateByTime": aggregate_by_time,
            "type": "userFills",
            "user": address,
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            user_fills = response.json()

            # Cache the data
            with open(cache_path, "w") as f:
                json.dump(user_fills, f, indent=4)

            return user_fills

        except requests.RequestException as e:
            logger.error(f"Failed to fetch user fills for {address}: {e}")
            raise


def get_user_fills_dataframe(
    address: str, use_cache: bool = True, aggregate_by_time: bool = True
) -> pl.DataFrame:
    """
    Load user fills into a Polars DataFrame.

    Args:
        address: User address to fetch fills for
        use_cache: Whether to use cached data if available
        aggregate_by_time: Whether to aggregate fills by time

    Returns:
        Polars DataFrame containing user fills data
    """

    user_fills = get_user_fills_json(address, use_cache, aggregate_by_time)

    if not user_fills:
        logger.warning(f"No user fills found for address {address}")
        return pl.DataFrame(schema=user_fills_schema)

    # Convert user fills to DataFrame rows
    rows = []
    for fill in user_fills:
        rows.append(
            {
                "time": int(fill["time"]),
                "coin": fill.get("coin", ""),
                "px": float(fill.get("px", 0.0)),
                "sz": float(fill.get("sz", 0.0)),
                "side": fill.get("side", ""),
                "startPosition": float(fill.get("startPosition", 0.0)),
                "dir": fill.get("dir", ""),
                "closedPnl": float(fill.get("closedPnl", 0.0)),
                "hash": fill.get("hash", ""),
                "oid": int(fill.get("oid", 0)),
                "crossed": fill.get("crossed", False),
                "fee": float(fill.get("fee", 0.0)),
                "tid": int(fill.get("tid", 0)),
                "feeToken": fill.get("feeToken", ""),
                "twapId": fill.get("twapId", None),
            }
        )

    df = pl.DataFrame(rows, schema_overrides=user_fills_schema)
    logger.debug(f"User fills DataFrame shape: {df.shape}")
    return df
