from loguru import logger
from models.class_models.explorer import UpdateLeverageModel
from models.class_models.state import PerpPositionModel, StateModel, StateUpdateModel
from models.class_models.user_ledger_updates import TxModel
from transformer.state import state_update
from constants.coin_id import coin_id_map

def user_leverage_update(state: StateModel, leverage_update: UpdateLeverageModel) -> StateModel:
    time = leverage_update.datetime
    token = coin_id_map.get(str(leverage_update.asset), leverage_update.asset)
    new_state_update = StateUpdateModel(
        time=int(time.timestamp() * 1000),
        token=token,
        is_perp=True,
        delta=0.0  # No change in size or balance, just updating leverage
    )
    # state_updates = [new_state_update]
    new_state = state_update(state, new_state_update)
    
    # Update the leverage in the perp position if it exists
    new_state.perp_positions[token].leverage = leverage_update.leverage
    
    return new_state