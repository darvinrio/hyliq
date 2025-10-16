import polars as pl

delta_type_enum = pl.Enum(
    [
        "accountClassTransfer",
        "spotTransfer",
        "cStakingTransfer",
        "withdraw",
        "internalTransfer",
        "deposit",
        "accountActivationGas",
    ]
)
# Schema for user non-funding ledger updates data
# This schema accommodates all the different delta types in the ledger updates
user_ledger_updates_schema = pl.Schema(
    {
        "time": pl.Datetime("ms"),
        "hash": pl.String,
        "delta_type": delta_type_enum,
        # Common fields across most delta types
        "usdc": pl.Float64,
        "token": pl.String,
        "amount": pl.Float64,
        "usdcValue": pl.Float64,
        "user": pl.String,
        "destination": pl.String,
        "fee": pl.Float64,
        "nativeTokenFee": pl.Float64,
        "nonce": pl.Int64,
        "feeToken": pl.String,
        # Specific fields for certain delta types
        "toPerp": pl.Boolean,  # accountClassTransfer
        "isDeposit": pl.Boolean,  # cStakingTransfer
    }
)
