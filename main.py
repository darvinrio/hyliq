from loguru import logger
import polars as pl

from config import REFRESH

from loaders import user_fills
from loaders.twap import  get_twap_history_pydantic
from loaders.user_fills import get_user_fills_pydantic
from loaders.user_funding import  get_user_funding_pydantic
from loaders.user_ledger_updates import get_user_ledger_updates_pydantic

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
    
    twaps = get_twap_history_pydantic(addr, use_cache=not REFRESH)
    user_fills = get_user_fills_pydantic(addr, use_cache=not REFRESH)
    user_funding = get_user_funding_pydantic(addr, use_cache=not REFRESH)
    user_ledger_updates = get_user_ledger_updates_pydantic(addr, use_cache=not REFRESH)
    
    print(twaps)
    print(user_fills)
    print(user_funding)
    print(user_ledger_updates)
    
    

    
    



