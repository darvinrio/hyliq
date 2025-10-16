from models.class_models.user_fills import UserFillsModel
from models.class_models.state import StateModel, StateUpdate
from transformer.state import state_update

def user_fill(state: StateModel, fill: UserFillsModel) -> StateModel:
    time = fill.datetime
    side = fill.side
    sz = fill.sz if side == "b" else -fill.sz
    is_perp = True if fill.dir in ["Open Long", "Open Short", "Close Long", "Close Short"] else False
    token = fill.coin
    delta = sz if fill.dir in ["Open Long", "Open Short", "Buy"] else -sz
    ntl = sz * fill.price if side == "b" else -sz * fill.price
    usdc_ntl = sz * fill.price
    
    state_updates = [
        StateUpdate(
            time=int(time.timestamp() * 1000),
            token=token,
            is_perp=is_perp,
            delta=delta
        ),
        StateUpdate(
            time=int(time.timestamp() * 1000),
            token="USDC",
            is_perp=is_perp,
            delta= usdc_ntl
        )
    ]
    
    new_state = state.deepcopy()
    for update in state_updates:
        new_state = state_update(new_state, update)
        
    return new_state