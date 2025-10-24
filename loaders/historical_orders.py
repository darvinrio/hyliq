from typing import List
import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.df_models.historical_orders import historical_orders_schema
from models.class_models.historical_orders import HistoricalOrderModel


def get_historical_orders_json(address: str, use_cache: bool = True) -> list:
    """
    Fetch historical orders from the Hyperliquid API.

    Args:
        address: User address to fetch historical orders for
        use_cache: Whether to use cached data if available

    Returns:
        List containing historical orders data from the API
    """

    historical_orders_dir = os.path.join(cache_dir, "historical_orders")
    os.makedirs(historical_orders_dir, exist_ok=True)

    cache_path = os.path.join(historical_orders_dir, f"{address.lower()}_historical_orders.json")

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
        payload = {"type": "historicalOrders", "user": address}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            historical_orders = response.json()

            # Cache the data
            with open(cache_path, "w") as f:
                json.dump(historical_orders, f, indent=4)

            return historical_orders

        except requests.RequestException as e:
            logger.error(f"Failed to fetch historical orders for {address}: {e}")
            raise


def get_historical_orders_dataframe(address: str, use_cache: bool = True) -> pl.DataFrame:
    """
    Load historical orders into a Polars DataFrame.

    Args:
        address: User address to fetch historical orders for
        use_cache: Whether to use cached data if available

    Returns:
        Polars DataFrame containing historical orders data
    """

    historical_orders = get_historical_orders_json(address, use_cache)

    if not historical_orders:
        logger.warning(f"No historical orders found for address {address}")
        return pl.DataFrame(schema=historical_orders_schema)

    # Convert historical orders to DataFrame rows
    rows = []
    for order_entry in historical_orders:
        order = order_entry.get("order", {})

        rows.append(
            {
                # Order details
                "coin": order.get("coin", ""),
                "side": order.get("side", ""),
                "limitPx": float(order.get("limitPx", 0.0)),
                "sz": float(order.get("sz", 0.0)),
                "oid": int(order.get("oid", 0)),
                "timestamp": int(order.get("timestamp", 0)),
                "triggerCondition": order.get("triggerCondition", ""),
                "isTrigger": order.get("isTrigger", False),
                "triggerPx": float(order.get("triggerPx", 0.0)),
                "isPositionTpsl": order.get("isPositionTpsl", False),
                "reduceOnly": order.get("reduceOnly", False),
                "orderType": order.get("orderType", ""),
                "origSz": float(order.get("origSz", 0.0)),
                "tif": order.get("tif", ""),
                "cloid": order.get("cloid", ""),
                # Status details
                "status": order_entry.get("status", ""),
                "statusTimestamp": int(order_entry.get("statusTimestamp", 0)),
            }
        )

    df = pl.DataFrame(rows, schema_overrides=historical_orders_schema)
    logger.debug(f"Historical orders DataFrame shape: {df.shape}")
    return df


def get_historical_orders_pydantic(address: str, use_cache: bool = True) -> List[HistoricalOrderModel]:
    """
    Load historical orders into a list of Pydantic models.

    Args:
        address: User address to fetch historical orders for
        use_cache: Whether to use cached data if available

    Returns:
        List of HistoricalOrderModel instances containing historical orders data
    """
    historical_orders = get_historical_orders_json(address, use_cache)

    if not historical_orders:
        logger.warning(f"No historical orders found for address {address}")
        return []

    models: List[HistoricalOrderModel] = []
    for order_entry in historical_orders:
        try:
            order = order_entry.get("order", {})

            model = HistoricalOrderModel(
                coin=order.get("coin", ""),
                side=order.get("side", "").lower(),
                limitPx=float(order.get("limitPx")),
                sz=float(order.get("sz")),
                oid=int(order.get("oid")),
                timestamp=int(order.get("timestamp")),
                triggerCondition=order.get("triggerCondition", ""),
                isTrigger=order.get("isTrigger", False),
                triggerPx=float(order.get("triggerPx")),
                isPositionTpsl=order.get("isPositionTpsl", False),
                reduceOnly=order.get("reduceOnly", False),
                orderType=order.get("orderType", ""),
                origSz=float(order.get("origSz")),
                tif=order.get("tif", ""),
                cloid=order.get("cloid"),
                status=order_entry.get("status", ""),
                statusTimestamp=int(order_entry.get("statusTimestamp")),
            )
            models.append(model)
        except Exception as e:
            logger.error(f"Error parsing historical order entry for address {address}: {e}")
            continue

    logger.debug(f"Parsed {len(models)} historical order models for address {address}")
    return models