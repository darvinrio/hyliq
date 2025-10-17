from models.class_models.twap import TWAPModel
from models.class_models.state import StateModel, StateUpdateModel
from transformer.state import state_update

def twap_state_update(state: StateModel, twap: TWAPModel) -> StateModel:
    if twap.status == "activated":
        return state
    
    time = twap.time
    side = twap.side
    sz = twap.sz if side == "b" else -twap.sz
    token = twap.coin
    is_perp = False if token[0] == "@" else True
    delta = twap.executedSz if side == "b" else -twap.executedSz
    # ntl = twap.executedNtl if side == "b" else -twap.executedNtl
    # usdc_ntl =  ntl if not is_perp else -ntl
    
    usdc_ntl = 0
    if is_perp:
        leverage = state.perp_positions.get(token).leverage
        usdc_ntl = -twap.executedNtl/leverage
    else:
        usdc_ntl = -twap.executedNtl if side == "b" else twap.executedNtl
    
    state_updates = [
        StateUpdateModel(
            time=int(time * 1000),
            token=token,
            is_perp=is_perp,
            delta=delta
        ),
        StateUpdateModel(
            time=int(time * 1000),
            token="USDC",
            is_perp=is_perp,
            delta= usdc_ntl
        )
    ]
    
    new_state = state.model_copy(deep=True)
    for update in state_updates:
        new_state = state_update(new_state, update)
        
    return new_state