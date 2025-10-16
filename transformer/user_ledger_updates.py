import stat

from loguru import logger
from models.class_models.state import StateModel, StateUpdateModel
from models.class_models.user_ledger_updates import TxModel
from transformer.state import state_update

def user_ledger_update(state: StateModel, ledger_entry: TxModel) -> StateModel:
    
    time = ledger_entry.datetime
    type = ledger_entry.delta.type
    state_updates = []
    
    if type == "deposit":
        new_state_update = StateUpdateModel(
            time=int(time.timestamp() * 1000),
            token="USDC",
            is_perp=False,
            delta=ledger_entry.delta.usdc
        )
        state_updates.append(new_state_update)
        
    elif type == "withdraw":
        new_state_update = StateUpdateModel(
            time=int(time.timestamp() * 1000),
            token="USDC",
            is_perp=False,
            delta=-ledger_entry.delta.usdc
        )
        state_updates.append(new_state_update)
        
    elif type == "internalTransfer":
        # transfer out
        if ledger_entry.delta.user == state.user:
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token="USDC",
                is_perp=False,
                delta=-ledger_entry.delta.usdc
            )
            state_updates.append(new_state_update)
        # transfer in
        elif ledger_entry.delta.destination == state.user:
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token="USDC",
                is_perp=False,
                delta=ledger_entry.delta.usdc
            )
            state_updates.append(new_state_update)
            
    elif type == "accountClassTransfer":
        # transfer from spot to perp
        if ledger_entry.delta.toPerp:
            # transfer out of spot
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token="USDC",
                is_perp=False,
                delta=-ledger_entry.delta.usdc
            )
            state_updates.append(new_state_update)
            # transfer into perp
            new_state_update_2 = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token="USDC",
                is_perp=True,
                delta=ledger_entry.delta.usdc
            )
            state_updates.append(new_state_update_2)
        # transfer from perp to spot
        else:
            # transfer out of perp
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token="USDC",
                is_perp=True,
                delta=-ledger_entry.delta.usdc
            )
            state_updates.append(new_state_update)
            # transfer into spot
            new_state_update_2 = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token="USDC",
                is_perp=False,
                delta=ledger_entry.delta.usdc
            )
            state_updates.append(new_state_update_2)
            
    elif type == "spotTransfer":
        # transfer out
        if ledger_entry.delta.user == state.user:
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token=ledger_entry.delta.token,
                is_perp=False,
                delta=-ledger_entry.delta.amount
            )
            state_updates.append(new_state_update)
        # transfer in
        elif ledger_entry.delta.destination == state.user:
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token=ledger_entry.delta.token,
                is_perp=False,
                delta=ledger_entry.delta.amount
            )
            state_updates.append(new_state_update)
    
    elif type == "cStakingTransfer":
        # deposit (stake)
        if ledger_entry.delta.isDeposit:
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token=ledger_entry.delta.token,
                is_perp=False,
                delta=ledger_entry.delta.amount
            )
            state_updates.append(new_state_update)
        # withdrawal (unstake)
        else:
            new_state_update = StateUpdateModel(
                time=int(time.timestamp() * 1000),
                token=ledger_entry.delta.token,
                is_perp=False,
                delta=-ledger_entry.delta.amount
            )
            state_updates.append(new_state_update)
            
    elif type == "accountActivationGas":
        new_state_update = StateUpdateModel(
            time=int(time.timestamp() * 1000),
            token=ledger_entry.delta.token,
            is_perp=False,
            delta=-ledger_entry.delta.amount
        )
        state_updates.append(new_state_update)
        
    else:
        logger.error(f"Unknown ledger update type: {type} in transaction {ledger_entry.hash}")
    
    new_state = state.model_copy(deep=True)
    for update in state_updates:
        new_state = state_update(new_state, update)
        
    return new_state