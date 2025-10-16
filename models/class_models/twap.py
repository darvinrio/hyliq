from pydantic import BaseModel, Field
from datetime import datetime, timezone
from models.class_models.common import OrderSide


class TWAPModel(BaseModel):
    """
    Time-Weighted Average Price (TWAP) Model

    Attributes:
        interval (int): The time interval in seconds over which to calculate the TWAP.
        start_time (str): The start time for the TWAP calculation in ISO 8601 format.
        end_time (str): The end time for the TWAP calculation in ISO 8601 format.
    """

    time: int = Field(..., description="Timestamp in milliseconds")
    coin: str = Field(..., description="Coin symbol")
    user: str = Field(..., description="User address")
    side: OrderSide = Field(..., description="Order side: 'b' for buy, 'a' for sell")
    sz: float = Field(..., description="Order size")
    executedSz: float = Field(..., description="Executed size")
    executedNtl: float = Field(..., description="Executed notional value")
    minutes: int = Field(..., description="Duration in minutes")
    reduceOnly: bool = Field(..., description="Whether the order is reduce-only")
    randomize: bool = Field(..., description="Whether the order is randomized")
    timestamp: int = Field(..., description="Order timestamp")
    status: str = Field(..., description="Order status")
    twapId: int | None = Field(None, description="TWAP order ID")

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.time / 1000, tz=timezone.utc)
