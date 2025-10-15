from loguru import logger
import polars as pl

from loaders.twap import get_twap_history_dataframe
from loaders.user_fills import get_user_fills_dataframe
from loaders.user_funding import get_user_funding_dataframe
from loaders.user_ledger_updates import get_user_ledger_updates_dataframe

dnhype_short_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
dnhype_spot_eoa = "0xca36897cd0783a558f46407cd663d0f46d2f3386"

eoas = [
    {"address": dnhype_short_eoa, "label": "DN Hype Short"},
    {"address": dnhype_spot_eoa, "label": "DN Hype Spot"},
]


for eoa in eoas:
    addr = eoa["address"]
    label = eoa["label"]
    logger.info(f"Processing {label} - {addr}")
    filename_uid = f"{label.replace(' ','_').lower()}"

    twap_df = get_twap_history_dataframe(addr)
    twap_df.write_csv(f"debug/{filename_uid}_twap.csv")

    fills_df = get_user_fills_dataframe(addr)
    fills_df.write_csv(f"debug/{filename_uid}_fills.csv")

    funding_df = get_user_funding_dataframe(addr)
    funding_df.write_csv(f"debug/{filename_uid}_funding.csv")

    ledger_updates_df = get_user_ledger_updates_dataframe(addr)
    ledger_updates_df.write_csv(f"debug/{filename_uid}_ledger_updates.csv")



