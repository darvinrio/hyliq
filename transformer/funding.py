from loguru import logger
from models.class_models.user_funding import UserFundingModel
from models.class_models.state import StateModel, StateUpdateModel
from transformer.state import state_update
from constants.coin_id import coin_id_map


def funding_state_update(state: StateModel, funding: UserFundingModel) -> StateModel:

    time = funding.time
    usdc = funding.usdc
    is_perp = True
    
    state_updates = [
        StateUpdateModel(
            time=int(time * 1000), token="USDC", is_perp=is_perp, delta=usdc
        ),
    ]

    new_state = state.model_copy(deep=True)
    for update in state_updates:
        new_state = state_update(new_state, update)

    return new_state
