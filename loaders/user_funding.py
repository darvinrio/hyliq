import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.df_models.user_funding import user_funding_schema


def get_user_funding_json(address: str, use_cache: bool = True) -> list:
    """
    Fetch user funding from the Hyperliquid API.

    Args:
        address: User address to fetch funding for
        use_cache: Whether to use cached data if available

    Returns:
        List containing user funding data from the API
    """

    user_funding_dir = os.path.join(cache_dir, "user_funding")
    os.makedirs(user_funding_dir, exist_ok=True)

    cache_path = os.path.join(user_funding_dir, f"{address.lower()}_user_funding.json")

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
        payload = {"type": "userFunding", "user": address}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            user_funding = response.json()

            # Cache the data
            with open(cache_path, "w") as f:
                json.dump(user_funding, f, indent=4)

            return user_funding

        except requests.RequestException as e:
            logger.error(f"Failed to fetch user funding for {address}: {e}")
            raise


def get_user_funding_dataframe(address: str, use_cache: bool = True) -> pl.DataFrame:
    """
    Load user funding into a Polars DataFrame.

    Args:
        address: User address to fetch funding for
        use_cache: Whether to use cached data if available

    Returns:
        Polars DataFrame containing user funding data
    """

    user_funding = get_user_funding_json(address, use_cache)

    if not user_funding:
        logger.warning(f"No user funding found for address {address}")
        return pl.DataFrame(schema=user_funding_schema)

    # Convert user funding to DataFrame rows
    rows = []
    for funding in user_funding:
        delta = funding.get("delta", {})

        rows.append(
            {
                "time": int(funding["time"]),
                "hash": funding.get("hash", ""),
                "delta_type": delta.get("type", ""),
                "coin": delta.get("coin", ""),
                "usdc": float(delta.get("usdc", 0.0)),
                "szi": float(delta.get("szi", 0.0)),
                "fundingRate": float(delta.get("fundingRate", 0.0)),
                "nSamples": delta.get("nSamples", None),
            }
        )

    df = pl.DataFrame(rows, schema_overrides=user_funding_schema)
    logger.debug(f"User funding DataFrame shape: {df.shape}")
    return df
