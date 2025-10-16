from turtle import mode
from typing import List
import requests
import json
import os
import polars as pl
from loguru import logger
from config import cache_dir
from models.class_models.user_ledger_updates import (
    AccountActivationGasTxModel,
    AccountClassTransferTxModel,
    CStakingTransferTxModel,
    DepositTxModel,
    InternalTransferTxModel,
    SpotTransferTxModel,
    TxModel,
    WithdrawTxModel,
)
from models.df_models.user_ledger_updates import user_ledger_updates_schema


def get_user_ledger_updates_json(address: str, use_cache: bool = True) -> list:
    """
    Fetch user non-funding ledger updates from the Hyperliquid API.

    Args:
        address: User address to fetch ledger updates for
        use_cache: Whether to use cached data if available

    Returns:
        List containing user ledger updates data from the API
    """

    ledger_updates_dir = os.path.join(cache_dir, "user_ledger_updates")
    os.makedirs(ledger_updates_dir, exist_ok=True)

    cache_path = os.path.join(
        ledger_updates_dir, f"{address.lower()}_ledger_updates.json"
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
        payload = {"type": "userNonFundingLedgerUpdates", "user": address}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            ledger_updates = response.json()

            # Cache the data
            with open(cache_path, "w") as f:
                json.dump(ledger_updates, f, indent=4)

            return ledger_updates

        except requests.RequestException as e:
            logger.error(f"Failed to fetch user ledger updates for {address}: {e}")
            raise


def get_user_ledger_updates_dataframe(
    address: str, use_cache: bool = True
) -> pl.DataFrame:
    """
    Load user non-funding ledger updates into a Polars DataFrame.

    Args:
        address: User address to fetch ledger updates for
        use_cache: Whether to use cached data if available

    Returns:
        Polars DataFrame containing user ledger updates data
    """

    ledger_updates = get_user_ledger_updates_json(address, use_cache)

    if not ledger_updates:
        logger.warning(f"No user ledger updates found for address {address}")
        return pl.DataFrame(schema=user_ledger_updates_schema)

    # Convert ledger updates to DataFrame rows
    rows = []
    for update in ledger_updates:
        delta = update.get("delta", {})

        # Extract common fields with defaults
        row = {
            "time": int(update["time"]),
            "hash": update.get("hash", ""),
            "delta_type": delta.get("type", ""),
            # Common fields
            "usdc": (
                float(delta.get("usdc", 0.0)) if delta.get("usdc") is not None else None
            ),
            "token": delta.get("token", ""),
            "amount": (
                float(delta.get("amount", 0.0))
                if delta.get("amount") is not None
                else None
            ),
            "usdcValue": (
                float(delta.get("usdcValue", 0.0))
                if delta.get("usdcValue") is not None
                else None
            ),
            "user": delta.get("user", ""),
            "destination": delta.get("destination", ""),
            "fee": (
                float(delta.get("fee", 0.0)) if delta.get("fee") is not None else None
            ),
            "nativeTokenFee": (
                float(delta.get("nativeTokenFee", 0.0))
                if delta.get("nativeTokenFee") is not None
                else None
            ),
            "nonce": delta.get("nonce", None),
            "feeToken": delta.get("feeToken", ""),
            # Specific fields
            "toPerp": delta.get("toPerp", None),
            "isDeposit": delta.get("isDeposit", None),
        }

        rows.append(row)

    df = pl.DataFrame(rows, schema_overrides=user_ledger_updates_schema)
    logger.debug(f"User ledger updates DataFrame shape: {df.shape}")
    return df


def get_user_ledger_updates_pydantic(
    address: str, use_cache: bool = True
) -> List[TxModel]:
    """
    Load user non-funding ledger updates into a list of Pydantic models.

    Args:
        address: User address to fetch ledger updates for
        use_cache: Whether to use cached data if available
    Returns:
        List of TxModel instances containing user ledger updates data
    """

    ledger_updates = get_user_ledger_updates_json(address, use_cache)

    if not ledger_updates:
        logger.warning(f"No user ledger updates found for address {address}")
        return pl.DataFrame(schema=user_ledger_updates_schema)

    models: List[TxModel] = []
    for update in ledger_updates:
        try:

            time = int(update.get("time"))
            hash = update.get("hash")
            delta = update.get("delta")
            type = delta.get("type")

            if type == "deposit":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=DepositTxModel(
                        type="deposit", usdc=float(delta.get("usdc", 0.0))
                    ),
                )

                models.append(model)

            elif type == "withdraw":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=WithdrawTxModel(
                        type="withdraw",
                        usdc=float(delta.get("usdc", 0.0)),
                        nonce=delta.get("nonce"),
                        fee=float(delta.get("fee", 0.0)),
                    ),
                )

                models.append(model)

            elif type == "internalTransfer":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=InternalTransferTxModel(
                        type="internalTransfer",
                        usdc=float(delta.get("usdc", 0.0)),
                        user=delta.get("user"),
                        destination=delta.get("destination"),
                        fee=float(delta.get("fee", 0.0)),
                    ),
                )

                models.append(model)

            elif type == "accountClassTransfer":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=AccountClassTransferTxModel(
                        type="accountClassTransfer",
                        usdc=float(delta.get("usdc", 0.0)),
                        toPerp=delta.get("toPerp"),
                    ),
                )

                models.append(model)

            elif type == "spotTransfer":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=SpotTransferTxModel(
                        type="spotTransfer",
                        token=delta.get("token"),
                        amount=float(delta.get("amount", 0.0)),
                        usdcValue=float(delta.get("usdcValue", 0.0)),
                        user=delta.get("user"),
                        destination=delta.get("destination"),
                        fee=float(delta.get("fee", 0.0)),
                        nativeTokenFee=float(delta.get("nativeTokenFee", 0.0)),
                    ),
                )

                models.append(model)

            elif type == "cStakingTransfer":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=CStakingTransferTxModel(
                        type="cStakingTransfer",
                        token=delta.get("token"),
                        amount=float(delta.get("amount", 0.0)),
                        isDeposit=delta.get("isDeposit"),
                    ),
                )

                models.append(model)

            elif type == "accountActivationGas":
                model = TxModel(
                    time=time,
                    hash=hash,
                    delta=AccountActivationGasTxModel(
                        type="accountActivationGas",
                        amount=float(delta.get("amount", 0.0)),
                        token=delta.get("token"),
                    ),
                )

                models.append(model)

            else:
                logger.error(
                    f"Unknown ledger update type: {type} in transaction {hash}"
                )
                continue

        except Exception as e:
            logger.error(f"Error processing ledger update {update}: {e}")
            continue

    logger.debug(f"Parsed {len(models)} ledger update models for address {address}")
    return models
