from typing import List
import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.class_models.user_fills import UserFillsModel
from models.df_models.user_fills import user_fills_schema


def get_user_fills_extended_json(
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

    user_fills_dir = os.path.join(cache_dir, "user_fills_extended")
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
            "type": "userFillsByTime",
            "user": address,
            "startTime": 0,
            # "endTime": 9999999999 * 1000,
            "endTime": 1747224124296,
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


def get_user_fills_extended_pydantic(
    address: str, use_cache: bool = True, aggregate_by_time: bool = True
) -> List[UserFillsModel]:
    """
    Load user fills into a list of Pydantic models.

    Args:
        address: User address to fetch fills for
        use_cache: Whether to use cached data if available
        aggregate_by_time: Whether to aggregate fills by time

    Returns:
        List of UserFillsModel instances
    """

    user_fills = get_user_fills_extended_json(address, use_cache, aggregate_by_time)

    if not user_fills:
        logger.warning(f"No user fills found for address {address}")
        return []

    # Convert user fills to list of Pydantic models
    models: List[UserFillsModel] = []
    for fill in user_fills:
        try:
            model = UserFillsModel(
                time=int(fill["time"]),
                coin=fill.get("coin"),
                px=float(fill.get("px")),
                sz=float(fill.get("sz")),
                side=fill.get("side").lower(),
                startPosition=float(fill.get("startPosition")),
                dir=fill.get("dir"),
                closedPnl=float(fill.get("closedPnl")),
                hash=fill.get("hash"),
                oid=int(fill.get("oid")) if fill.get("oid") is not None else None,
                crossed=fill.get("crossed"),
                fee=float(fill.get("fee")),
                tid=int(fill.get("tid")),
                feeToken=fill.get("feeToken"),
                twapId=(
                    int(fill.get("twapId")) if fill.get("twapId") is not None else None
                ),
            )
            models.append(model)
        except Exception as e:
            logger.error(f"Error parsing Fill entry into model: {e}")

    logger.debug(f"Parsed {len(models)} user fills into Pydantic models")
    return models
