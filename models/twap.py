import polars as pl

# Schema for TWAP history data
twap_schema = pl.Schema(
    {
        "time": pl.Datetime("ms"),
        "coin": pl.String,
        "user": pl.String,
        "side": pl.String,
        "sz": pl.Float64,
        "executedSz": pl.Float64,
        "executedNtl": pl.Float64,
        "minutes": pl.Int64,
        "reduceOnly": pl.Boolean,
        "randomize": pl.Boolean,
        "timestamp": pl.Datetime("ms"),
        "status": pl.String,
        "status_description": pl.String,
        "twapId": pl.Int64,
    }
)
