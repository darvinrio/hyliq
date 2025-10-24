import polars as pl

# Schema for historical orders data
historical_orders_schema = pl.Schema(
    {
        # Order details
        "coin": pl.String,
        "side": pl.String,
        "limitPx": pl.Float64,
        "sz": pl.Float64,
        "oid": pl.Int64,
        "timestamp": pl.Datetime("ms"),
        "triggerCondition": pl.String,
        "isTrigger": pl.Boolean,
        "triggerPx": pl.Float64,
        "isPositionTpsl": pl.Boolean,
        "reduceOnly": pl.Boolean,
        "orderType": pl.String,
        "origSz": pl.Float64,
        "tif": pl.String,
        "cloid": pl.String,
        # Status details
        "status": pl.String,
        "statusTimestamp": pl.Datetime("ms"),
    }
)