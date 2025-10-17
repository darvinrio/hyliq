from typing import Dict, List
from pydantic import BaseModel, Field


class SpotPositionModel(BaseModel):
    """
    Represents a spot position held by a user.
    """

    token: str = Field(..., description="The token symbol of the spot position.")
    balance: float = Field(..., description="The balance of the spot position.")
    usdc_value: float = Field(..., description="The USDC value of the spot position.")


class PerpPositionModel(BaseModel):
    """
    Represents a perp position held by a user.
    """

    token: str = Field(..., description="The token symbol of the perp position.")
    size: float = Field(..., description="The size of the perp position.")
    leverage: float = Field(10, description="The leverage of the perp position.")
    entry_price: float = Field(..., description="The entry price of the perp position.")
    usdc_value: float = Field(..., description="The USDC value of the perp position.")


class StateModel(BaseModel):
    """
    Represents the state of a user in the system.
    """

    user: str = Field(..., description="The wallet address of the user.")
    time: int = Field(..., description="The timestamp of the state record.")
    spot_usdc: float = Field(..., description="The spot USDC balance of the user.")
    perp_usdc: float = Field(..., description="The perpetual USDC balance of the user.")
    spot_positions: Dict[str, SpotPositionModel] = Field(
        default_factory=dict, description="Spot positions indexed by token symbol."
    )
    perp_positions: Dict[str, PerpPositionModel] = Field(
        default_factory=dict, description="Perp positions indexed by token symbol."
    )


class StateUpdateModel(BaseModel):
    """
    Represents an update to the user's state.
    """

    time: int = Field(..., description="The timestamp of the update.")
    token: str = Field(..., description="The token symbol for the update.")
    is_perp: bool = Field(..., description="Whether the update is for a perp position.")
    delta: float = Field(..., description="The change in size or balance.")
