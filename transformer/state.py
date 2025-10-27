from models.class_models.state import (
    PerpPositionModel,
    SpotPositionModel,
    StateModel,
    StateUpdateModel,
    VaultPositionModel,
)
from constants.coin_id import coin_id_map


def init_state(user: str, time: int) -> StateModel:
    return StateModel(
        user=user,
        time=time,
        spot_usdc=0.0,
        perp_usdc=0.0,
        spot_positions={},
        perp_positions={},
        vault_positions={},
    )


def state_update(state: StateModel, update: StateUpdateModel) -> StateModel:
    new_spot_positions = state.spot_positions.copy()
    new_perp_positions = state.perp_positions.copy()
    new_vault_positions = state.vault_positions.copy()
    new_spot_usdc = state.spot_usdc
    new_perp_usdc = state.perp_usdc

    token = coin_id_map.get(update.token, update.token)

    if token == "USDC":
        if update.is_perp:
            new_perp_usdc += update.delta
        elif update.is_vault:
            new_perp_usdc += -update.delta
        else:
            new_spot_usdc += update.delta
    else:
        if update.is_perp:
            if token in state.perp_positions:
                old_pos = state.perp_positions[token]
                new_perp_positions[token] = PerpPositionModel(
                    token=old_pos.token,
                    size=old_pos.size + update.delta,
                    leverage=old_pos.leverage,
                    entry_price=old_pos.entry_price,
                    usdc_value=old_pos.usdc_value,
                )
            else:
                new_perp_positions[token] = PerpPositionModel(
                    token=token, size=update.delta, leverage= 10, entry_price=0.0, usdc_value=0.0
                )
        else:
            if token in state.spot_positions:
                old_pos = state.spot_positions[token]
                # Create NEW position object with updated values
                new_spot_positions[token] = SpotPositionModel(
                    token=old_pos.token,
                    balance=old_pos.balance + update.delta,
                    usdc_value=old_pos.usdc_value,
                )
            else:
                new_spot_positions[token] = SpotPositionModel(
                    token=token, balance=update.delta, usdc_value=0.0
                )
                
    if update.is_vault:
        vault = update.vault
        if vault in state.vault_positions:
            old_pos = state.vault_positions[vault]
            new_vault_positions[vault] = VaultPositionModel(
                vault=old_pos.vault,
                balance=old_pos.balance + update.delta,
                usdc_value=old_pos.usdc_value,
            )
        else:
            new_vault_positions[vault] = VaultPositionModel(
                vault=vault, balance=update.delta, usdc_value=0.0
            )

    return StateModel(
        user=state.user,
        time=update.time,
        spot_usdc=new_spot_usdc,
        perp_usdc=new_perp_usdc,
        spot_positions=new_spot_positions,
        perp_positions=new_perp_positions,
        vault_positions=new_vault_positions,
    )
