import polars as pl

# Schema for user funding data
user_funding_schema = pl.Schema(
    {
        "time": pl.Datetime("ms"),
        "hash": pl.String,
        "delta_type": pl.String,
        "coin": pl.String,
        "usdc": pl.Float64,
        "szi": pl.Float64,
        "fundingRate": pl.Float64,
        "nSamples": pl.Int64,
    }
)
