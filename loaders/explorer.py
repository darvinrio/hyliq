from typing import List
import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.class_models.explorer import UpdateLeverageModel
from models.df_models.explorer import user_details_schema

# Global list of transaction types to filter out
FILTERED_TX_TYPES = ["evmRawTx"]


def get_user_explorer_json(
    address: str, use_cache: bool = True, filtered: bool = True
) -> dict:
    """
    Fetch user details from the Hyperliquid explorer API.

    Args:
        address: User address to fetch details for
        use_cache: Whether to use cached data if available
        filtered: Whether to return filtered data (without evmRawTx) or raw data

    Returns:
        Dictionary containing user details from the API
    """

    user_details_dir = os.path.join(cache_dir, "user_explorer")
    os.makedirs(user_details_dir, exist_ok=True)

    # Use different cache files for raw and filtered data
    if filtered:
        cache_path = os.path.join(user_details_dir, f"{address.lower()}_filtered.json")
    else:
        cache_path = os.path.join(user_details_dir, f"{address.lower()}_raw.json")

    if os.path.isfile(cache_path) and use_cache:
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        # Make API request to Hyperliquid explorer
        url = "https://rpc.hyperliquid.xyz/explorer"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            # 'Origin': 'https://app.hyperliquid.xyz',
            # 'Referer': 'https://app.hyperliquid.xyz/',
        }
        payload = {"type": "userDetails", "user": address}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            user_details = response.json()

            # Always cache the raw data first
            raw_cache_path = os.path.join(
                user_details_dir, f"{address.lower()}_raw.json"
            )
            with open(raw_cache_path, "w") as f:
                json.dump(user_details, f, indent=4)

            # Create filtered version if requested
            if filtered:
                filtered_data = user_details.copy()
                # Filter out transactions based on global FILTERED_TX_TYPES list
                if "txs" in filtered_data:
                    filtered_data["txs"] = [
                        tx
                        for tx in filtered_data["txs"]
                        if tx["action"].get("type") not in FILTERED_TX_TYPES
                    ]

                # Cache the filtered data
                with open(cache_path, "w") as f:
                    json.dump(filtered_data, f, indent=4)

                return filtered_data
            else:
                return user_details

        except requests.RequestException as e:
            logger.error(f"Failed to fetch user details for {address}: {e}")
            raise


def get_user_explorer_dataframe(address: str, use_cache: bool = True) -> pl.DataFrame:
    """
    Load user details into a Polars DataFrame.

    Args:
        address: User address to fetch details for
        use_cache: Whether to use cached data if available

    Returns:
        Polars DataFrame containing user transaction details
    """

    # Use filtered data by default (comment out filtered=True to use raw data)
    user_details = get_user_explorer_json(address, use_cache, filtered=True)
    # user_details = get_user_details_json(address, use_cache, filtered=False)  # Uncomment for raw data

    # Extract transactions from the response
    txs = user_details.get("txs", [])

    if not txs:
        logger.warning(f"No transactions found for address {address}")
        return pl.DataFrame(schema=user_details_schema)

    # Convert transactions to DataFrame rows, filtering out evmRawTx transactions
    rows = []
    for tx in txs:
        # Skip transactions with action type in FILTERED_TX_TYPES (only needed if using raw data)
        # if tx["action"].get("type") in FILTERED_TX_TYPES:
        #     continue

        rows.append(
            {
                "time": int(tx["time"]),
                "user": tx["user"],
                "action_type": tx["action"].get("type", ""),
                "action_data": tx["action"].get("data", ""),
                "block": int(tx["block"]),
                "hash": tx["hash"],
                "error": tx["error"] if tx["error"] is not None else "",
            }
        )

    df = pl.DataFrame(rows, schema_overrides=user_details_schema)
    logger.debug(f"User details DataFrame shape: {df.shape}")
    return df

def get_user_explorer_pydantic(
    address: str, use_cache: bool = True
)-> List[UpdateLeverageModel]:
    """
    Load user details into a list of Pydantic models.
    Currently only supports UpdateLeverageModel.

    Args:
        address: User address to fetch details for
        use_cache: Whether to use cached data if available

    Returns:
        List of UpdateLeverageModel instances containing user transaction details
    """
    
    # Use filtered data by default (comment out filtered=True to use raw data)
    user_details = get_user_explorer_json(address, use_cache, filtered=True)
    # user_details = get_user_details_json(address, use_cache, filtered=False)  # Uncomment for raw data

    # Extract transactions from the response
    txs = user_details.get("txs", [])

    if not txs:
        logger.warning(f"No transactions found for address {address}")
        return []

    models: List[UpdateLeverageModel] = []
    for tx in txs:
        try:
            time = int(tx["time"])
            user = tx["user"]
            block = int(tx["block"])
            hash = tx["hash"]
            error = tx["error"] if tx["error"] is not None else None

            action = tx.get("action", {})
            action_type = action.get("type", "")

            if action_type == "updateLeverage":
                model = UpdateLeverageModel(
                    time=time,
                    user=user,
                    asset=int(action.get("asset")),
                    isCross=bool(action.get("isCross")),
                    leverage=float(action.get("leverage")),
                    block=block,
                    hash=hash,
                    error=error,
                )
                models.append(model)

        except Exception as e:
            logger.error(f"Failed to parse transaction {tx}: {e}")
            continue

    return models