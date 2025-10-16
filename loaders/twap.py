from math import e
from typing import List
import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.class_models.twap import TWAPModel
from models.df_models.twap import twap_schema


def get_twap_history_json(address: str, use_cache: bool = True) -> list:
    """
    Fetch TWAP history from the Hyperliquid API.

    Args:
        address: User address to fetch TWAP history for
        use_cache: Whether to use cached data if available

    Returns:
        List containing TWAP history data from the API
    """

    twap_dir = os.path.join(cache_dir, "twap")
    os.makedirs(twap_dir, exist_ok=True)

    cache_path = os.path.join(twap_dir, f"{address.lower()}_twap_history.json")

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
        payload = {"type": "twapHistory", "user": address}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            twap_history = response.json()

            # Cache the data
            with open(cache_path, "w") as f:
                json.dump(twap_history, f, indent=4)

            return twap_history

        except requests.RequestException as e:
            logger.error(f"Failed to fetch TWAP history for {address}: {e}")
            raise


def get_twap_history_dataframe(address: str, use_cache: bool = True) -> pl.DataFrame:
    """
    Load TWAP history into a Polars DataFrame.

    Args:
        address: User address to fetch TWAP history for
        use_cache: Whether to use cached data if available

    Returns:
        Polars DataFrame containing TWAP history data
    """

    twap_history = get_twap_history_json(address, use_cache)

    if not twap_history:
        logger.warning(f"No TWAP history found for address {address}")
        return pl.DataFrame(schema=twap_schema)

    # Convert TWAP history to DataFrame rows
    rows = []
    for entry in twap_history:
        state = entry.get("state", {})
        status = entry.get("status", {})

        rows.append(
            {
                "time": int(entry["time"])*1000,
                "coin": state.get("coin", ""),
                "user": state.get("user", ""),
                "side": state.get("side", ""),
                "sz": float(state.get("sz", 0.0)),
                "executedSz": float(state.get("executedSz", 0.0)),
                "executedNtl": float(state.get("executedNtl", 0.0)),
                "minutes": int(state.get("minutes", 0)),
                "reduceOnly": state.get("reduceOnly", False),
                "randomize": state.get("randomize", False),
                "timestamp": int(state.get("timestamp", 0)),
                "status": status.get("status", ""),
                "status_description": status.get("description", ""),
                "twapId": entry.get("twapId", None),
            }
        )

    df = pl.DataFrame(rows, schema_overrides=twap_schema)
    logger.debug(f"TWAP history DataFrame shape: {df.shape}")
    return df

def get_twap_history_pydantic(address: str, use_cache: bool = True) -> List[TWAPModel]:
    """
    Load TWAP history into a list of Pydantic models.

    Args:
        address: User address to fetch TWAP history for
        use_cache: Whether to use cached data if available

    Returns:
        List of TWAPModel instances containing TWAP history data
    """
    twap_history = get_twap_history_json(address, use_cache)
    
    if not twap_history:
        logger.warning(f"No TWAP history found for address {address}")
        return []
    
    models: List[TWAPModel] = []
    for entry in twap_history:
        try:
            state = entry.get("state")
            status = entry.get("status")
            
            model = TWAPModel(
                time=int(entry["time"])*1000,
                coin=state.get("coin"),
                user=state.get("user"),
                side=state.get("side").lower(),
                sz=float(state.get("sz")),
                executedSz=float(state.get("executedSz")),
                executedNtl=float(state.get("executedNtl")),
                minutes=int(state.get("minutes")),
                reduceOnly=state.get("reduceOnly"),
                randomize=state.get("randomize"),
                timestamp=int(state.get("timestamp")),
                status=status.get("status"),
                twapId=entry.get("twapId", None)
            )
            models.append(model)
        except Exception as e:
            logger.error(f"Error parsing TWAP entry for address {address}: {e}")
            continue
    
    logger.debug(f"Parsed {len(models)} TWAP models for address {address}")
    return models