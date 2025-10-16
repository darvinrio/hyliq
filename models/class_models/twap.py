from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from models.class_models.common import OrderSide

class TwapStatus(str, Enum):
    f = "finished"
    a = "activated"
    t = "terminated"
    e = "error"
    
class TWAPModel(BaseModel):
    """
    Time-Weighted Average Price (TWAP) Model
    
    Attributes:
        time (int): The timestamp of the TWAP order in milliseconds.
        coin (str): The coin symbol.
        user (str): The user address.
        side (str): The order side: 'b' for buy, 'a' for sell.
        sz (float): The total order size.
        executedSz (float): The executed size of the order.
        executedNtl (float): The executed notional value.
        minutes (int): The duration of the TWAP order in minutes.
        reduceOnly (bool): Whether the order is reduce-only.
        randomize (bool): Whether the order is randomized.
        timestamp (int): The order timestamp.
        status (str): The status of the TWAP order.
        twapId (int | None): The TWAP order ID, if applicable.
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
    status: TwapStatus = Field(..., description="Order status")
    twapId: int | None = Field(None, description="TWAP order ID")

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.time / 1000, tz=timezone.utc)
