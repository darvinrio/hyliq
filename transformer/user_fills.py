from models.class_models.user_fills import UserFillsModel
from models.class_models.state import StateModel, StateUpdateModel
from transformer.state import state_update
from constants.coin_id import coin_id_map


def user_fill_state_update(state: StateModel, fill: UserFillsModel) -> StateModel:
    time = fill.datetime
    side = fill.side
    start_position = fill.startPosition
    sz = fill.sz if side == "b" else -fill.sz
    is_perp = (
        True
        if fill.dir
        in ["Open Long", "Open Short", "Close Long", "Close Short", "Auto-Deleveraging"]
        else False
    )
    token = coin_id_map.get(fill.coin, fill.coin)
    delta = sz
    # ntl = sz * fill.px if side == "b" else -sz * fill.px
    # usdc_ntl = ntl if not is_perp else -ntl

    usdc_ntl = 0
    if is_perp:
        leverage = 10
        try:
            leverage = state.perp_positions.get(token).leverage
        except: 
            pass
        usdc_ntl = -(sz * fill.px) / leverage
        if (start_position < 0 and delta > 0) or (start_position > 0 and delta < 0):
            print(usdc_ntl, "flipped")
            usdc_ntl = -usdc_ntl
    else:
        usdc_ntl = -(fill.sz * fill.px) if side == "b" else (fill.sz * fill.px)

    state_updates = [
        StateUpdateModel(
            time=int(time.timestamp() * 1000), token=token, is_perp=is_perp, delta=delta
        ),
        StateUpdateModel(
            time=int(time.timestamp() * 1000),
            token="USDC",
            is_perp=is_perp,
            delta=usdc_ntl,
        ),
    ]

    new_state = state.model_copy(deep=True)
    for update in state_updates:
        new_state = state_update(new_state, update)

    return new_state
