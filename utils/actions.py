import polars as pl
import os
import json
from config import cache_dir


def get_actions(address: str, use_cache: bool = True) -> pl.DataFrame:
    actions_dir = os.path.join("src")
    os.makedirs(actions_dir, exist_ok=True)
    actions_file = os.path.join(actions_dir, f"{address.lower()}.csv")
    df_actions = pl.read_csv(actions_file, infer_schema_length=0)
    return df_actions
