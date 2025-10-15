import polars as pl

# Schema for user details transactions
user_details_schema = pl.Schema({
    "time": pl.Datetime("ms"),
    "user": pl.String,
    "action_type": pl.String,
    "action_data": pl.String,
    "block": pl.Int64,
    "hash": pl.String,
    "error": pl.String,
})