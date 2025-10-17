from hmac import new
import json
from turtle import up
from loguru import logger
import polars as pl

from config import REFRESH

from loaders.explorer import get_user_explorer_pydantic
from loaders.twap import get_twap_history_pydantic
from loaders.user_fills import get_user_fills_pydantic
from loaders.user_funding import get_user_funding_pydantic
from loaders.user_ledger_updates import get_user_ledger_updates_pydantic
from models.class_models.explorer import UpdateLeverageModel
from models.class_models.twap import TWAPModel
from models.class_models.user_fills import UserFillsModel
from models.class_models.user_ledger_updates import TxModel
from transformer.explorer import user_leverage_update
from transformer.state import init_state
from transformer.user_fills import user_fill_state_update
from transformer.user_ledger_updates import user_ledger_update
from transformer.twap import twap_state_update
from datetime import datetime

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
    leverage_updates = get_user_explorer_pydantic(addr, use_cache=not REFRESH)

    # print(twaps)
    # print(user_fills)
    # print(user_funding)
    # print(user_ledger_updates)

    updates = [
        *twaps,
        # *user_funding,
        *user_fills,
        *user_ledger_updates,
        *leverage_updates,
    ]

    updates = sorted(updates, key=lambda x: x.time)
    initial_state = init_state(addr.lower(), 0)
    new_state = initial_state.model_copy(deep=True)
    print("[")
    out = []
    for update in updates:
        # try:
        if isinstance(update, TxModel):
            new_state = user_ledger_update(new_state, update)
        elif isinstance(update, TWAPModel):
            new_state = twap_state_update(new_state, update)
        elif isinstance(update, UserFillsModel):
            new_state = user_fill_state_update(new_state, update)
        elif isinstance(update, UpdateLeverageModel):
            new_state = user_leverage_update(new_state, update)
        else:
            logger.error(f"Unknown update type: {type(update)}")
            continue

        # except Exception as e:
        #     logger.error(f"Error processing {update.name} update at {update.time} - {e}")
        #     continue
        dt = datetime.fromtimestamp(update.time / 1000)
        out += [
            {
                "time": update.time,
                "update": update.model_dump(),
                "new_state": new_state.model_dump(),
            }
        ]
        print(
            json.dumps(
                {
                    "time": update.time,
                    "update": update.model_dump(),
                    "new_state": new_state.model_dump(),
                }
            )
        )
        print(",")
    print("]")
    logger.success(f"Final state for {label}: {new_state.model_dump_json(indent=2)}")

    with open(f"user_state_{filename_uid}.json", "w") as f:
        json.dump(out, f, indent=2)
