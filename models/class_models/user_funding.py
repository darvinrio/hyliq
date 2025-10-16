from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone
from models.class_models.common import OrderSide


class UserFundingModel(BaseModel):
    """
    User Funding Model

    Attributes:
        time (int): The timestamp of the funding event in milliseconds.
        coin (str): The coin symbol.
        user (str): The user address.
        funding (float): The funding amount.
        position (float): The user's position size at the time of funding.
        rate (float): The funding rate applied.
    """

    name: str = "UserFunding"
    time: int = Field(..., description="Timestamp in milliseconds")
    hash: str = Field(..., description="Transaction hash")
    delta_type: str = Field(..., description="Type of funding delta")
    coin: str = Field(..., description="Coin symbol")
    usdc: float = Field(..., description="Funding amount in USDC")
    szi: float = Field(..., description="User's position size at funding time")
    fundingRate: float = Field(..., description="Funding rate applied")
    nSamples: int | None = Field(
        ..., description="Number of samples used to calculate funding"
    )

    @property
    def datetime(self):
        """returns the datetime object corresponding to the funding time."""
        return datetime.fromtimestamp(self.time / 1000, tz=timezone.utc)
