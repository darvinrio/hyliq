from hmac import new
import json
from turtle import up
from loguru import logger
import polars as pl

from config import REFRESH

from loaders.explorer import get_user_explorer_pydantic
from loaders.historical_orders import get_historical_orders_pydantic
from loaders.twap import get_twap_history_pydantic
from loaders.user_fills import get_user_fills_pydantic
from loaders.user_funding import get_user_funding_pydantic
from loaders.user_ledger_updates import get_user_ledger_updates_pydantic
from models.class_models.explorer import UpdateLeverageModel
from models.class_models.twap import TWAPModel
from models.class_models.user_fills import UserFillsModel
from models.class_models.user_funding import UserFundingModel
from models.class_models.user_ledger_updates import TxModel
from transformer.explorer import user_leverage_update
from transformer.state import init_state
from transformer.user_fills import user_fill_state_update
from transformer.user_ledger_updates import user_ledger_update
from transformer.twap import twap_state_update
from transformer.funding import funding_state_update
from datetime import datetime

dnhype_short_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
dnhype_spot_eoa = "0xca36897cd0783a558f46407cd663d0f46d2f3386"

dnpump_short_eoa = "0xCA0Eb15d0efF480c15aC9071db8F47aF9b35ce98"
dnpump_spot_eoa = "0x975b62b498ed8369f781c2bd2e181ee53612a704"

hbusdt_deposit = "0xD317d8Bf73fCB1758bAA772819163B452D6e2b01"
hbusdt_onchain = "0x5064d3e2906317905f1d59663d5fa257c15a704a"
hbusdt_spot_1  = "0x1c020f03305acd09994c1910d440646e4a5f91b0"
hbusdt_spot_2 = "0xf545003323da8419ce95dd4137ec90577d420ea1"
hbusdt_withdrawal  = "0x77930A9cd3Db2A9e49f730Db8743bece140260C9"

dnhype_eoas = [
    {"address": dnhype_short_eoa, "label": "DN Hype Short"},
    # {"address": dnhype_spot_eoa, "label": "DN Hype Spot"},
    {"address": "0x364F7Fd945B8c76C3C77d6ac253f1fEa3B65E00d", "label": "DN Hype Spot"},
]
dnpump_eoas = [
    {"address": dnpump_short_eoa, "label": "DN Pump Short"},
    {"address": dnpump_spot_eoa, "label": "DN Pump Spot"},
]
hbusdt_eoas = [
    {"address": hbusdt_deposit, "label": "hbUSDT Deposit"},
    {"address": hbusdt_onchain, "label": "hbUSDT Onchain"},
    {"address": hbusdt_spot_1, "label": "hbUSDT Spot 1 "},
    {"address": hbusdt_spot_2, "label": "hbUSDT Spot 2"},
    {"address": hbusdt_withdrawal, "label": "hbUSDT Withdrawal"},
]

for eoa in dnhype_eoas:
    addr = eoa["address"]
    label = eoa["label"]
    logger.info(f"Processing {label} - {addr}")
    filename_uid = f"{label.replace(' ','_').lower()}"

    historical_orders = get_historical_orders_pydantic(addr, use_cache=not REFRESH)
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
        *user_funding,
        *user_fills,
        *user_ledger_updates,
        *leverage_updates,
    ]

    # # Check if there are any updates to process
    # if not updates:
    #     logger.warning(f"No transactions or updates found for {label} - {addr}. Skipping.")
    #     continue

    # logger.info(type(updates))
    updates = sorted(updates, key=lambda x: x.time)
    initial_state = init_state(addr.lower(), 0)
    new_state = initial_state.model_copy(deep=True)
    print("[")
    out = []
    for update in updates:
        # try:
        # logger.debug(f"processing {update.name} update at {update.time} for eoa {addr}")   
        if isinstance(update, TxModel):
            new_state = user_ledger_update(new_state, update)
        elif isinstance(update, TWAPModel):
            new_state = twap_state_update(new_state, update)
        elif isinstance(update, UserFillsModel):
            new_state = user_fill_state_update(new_state, update)
        elif isinstance(update, UpdateLeverageModel):
            new_state = user_leverage_update(new_state, update)
        elif isinstance(update, UserFundingModel):
            new_state = funding_state_update(new_state, update)
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
