from models.class_models.user_fills import UserFillsModel
from models.class_models.state import StateModel, StateUpdateModel
from transformer.state import state_update
from constants.coin_id import coin_id_map

def user_fill_state_update(state: StateModel, fill: UserFillsModel) -> StateModel:
    time = fill.datetime
    side = fill.side
    sz = fill.sz if side == "b" else -fill.sz
    is_perp = True if fill.dir in ["Open Long", "Open Short", "Close Long", "Close Short" , "Auto-Deleveraging"] else False
    token = fill.coin if fill.coin[0] != "@" else coin_id_map.get(fill.coin, fill.coin)
    delta = sz
    # ntl = sz * fill.px if side == "b" else -sz * fill.px
    # usdc_ntl = ntl if not is_perp else -ntl
    
    usdc_ntl = 0
    if is_perp:
        usdc_ntl = -(sz * fill.px)
    else:
        usdc_ntl = (sz * fill.px) if side == "b" else -(sz * fill.px)
    
    state_updates = [
        StateUpdateModel(
            time=int(time.timestamp() * 1000),
            token=token,
            is_perp=is_perp,
            delta=delta
        ),
        StateUpdateModel(
            time=int(time.timestamp() * 1000),
            token="USDC",
            is_perp=is_perp,
            delta= usdc_ntl
        )
    ]
    
    new_state = state.model_copy(deep=True)
    for update in state_updates:
        new_state = state_update(new_state, update)
        
    return new_state