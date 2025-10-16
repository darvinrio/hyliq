import re
import polars as pl
import os
from config import cache_dir
from cchecksum import to_checksum_address
from models.df_models.actions import actions_schema


def get_actions(address: str, use_cache: bool = True) -> pl.DataFrame:
    actions_dir = os.path.join("src")
    os.makedirs(actions_dir, exist_ok=True)
    file_name = f"{to_checksum_address(address)}"
    actions_file = os.path.join(actions_dir, f"{file_name}.csv")

    # Read CSV with proper null handling and increased schema inference
    df_actions = pl.read_csv(
        actions_file,
        schema_overrides={**actions_schema, "time": pl.Int64},  # Read as integer first
        null_values=["-", "", "null", "NULL"],
        infer_schema_length=10000,
    ).with_columns(
        [
            pl.col("time").cast(
                pl.Datetime("ms")
            )  # Convert from milliseconds timestamp to datetime
        ]
    )

    return df_actions


def generate_positions(
    address: str, use_cache: bool = True
) -> tuple[pl.DataFrame, pl.DataFrame]:

    actions_df = get_actions(address, use_cache)

    # Group by class and token, then calculate cumulative sum of amount
    hist_df = actions_df.sort("time").with_columns(
        [
            # pl.col("amount").cum_sum().over(["class", "token", "type"]).alias("cumulative_amount")
        ]
    )

    # Get the latest cumulative value for each class-token combination
    latest_df = hist_df.group_by(["class", "token", "type"]).agg(
        [
            pl.col("time").max().alias("latest_time"),
            # pl.col("cumulative_amount").last().alias("latest_position")
        ]
    )

    return hist_df, latest_df
