import polars as pl

# Schema for user fills data
user_fills_schema = pl.Schema(
    {
        "time": pl.Datetime("ms"),
        "coin": pl.String,
        "px": pl.Float64,
        "sz": pl.Float64,
        "side": pl.String,
        "startPosition": pl.Float64,
        "dir": pl.String,
        "closedPnl": pl.Float64,
        "hash": pl.String,
        "oid": pl.Int64,
        "crossed": pl.Boolean,
        "fee": pl.Float64,
        "tid": pl.Int64,
        "feeToken": pl.String,
        "twapId": pl.Int64,
    }
)
