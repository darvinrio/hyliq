from models.class_models.state import PerpPosition, SpotPosition, State, StateUpdate

def init_state(user: str, time: int) -> State:
    return State(
        user=user,
        time=time,
        spot_usdc=0.0,
        perp_usdc=0.0,
        spot_positions={},
        perp_positions={}
    )

def state_update(state: State, update: StateUpdate) -> State:
    new_spot_positions = state.spot_positions.copy()
    new_perp_positions = state.perp_positions.copy()
    new_spot_usdc = state.spot_usdc
    new_perp_usdc = state.perp_usdc
    
    if update.token == "USDC":
        if update.is_perp:
            new_perp_usdc += update.delta
        else:
            new_spot_usdc += update.delta
    else:
        if update.is_perp:
            if update.token in state.perp_positions:
                old_pos = state.perp_positions[update.token]
                new_perp_positions[update.token] = PerpPosition(
                    token=old_pos.token,
                    size=old_pos.size + update.delta,
                    entry_price=old_pos.entry_price,
                    usdc_value=old_pos.usdc_value
                )
            else:
                new_perp_positions[update.token] = PerpPosition(
                    token=update.token,
                    size=update.delta,
                    entry_price=0.0,
                    usdc_value=0.0
                )
        else:
            if update.token in state.spot_positions:
                old_pos = state.spot_positions[update.token]
                # Create NEW position object with updated values
                new_spot_positions[update.token] = SpotPosition(
                    token=old_pos.token,
                    balance=old_pos.balance + update.delta,
                    usdc_value=old_pos.usdc_value
                )
            else:
                new_spot_positions[update.token] = SpotPosition(
                    token=update.token,
                    balance=update.delta,
                    usdc_value=0.0
                )
    
    return State(
        user=state.user,
        time=update.time,
        spot_usdc=new_spot_usdc,
        perp_usdc=new_perp_usdc,
        spot_positions=new_spot_positions,
        perp_positions=new_perp_positions
    )
