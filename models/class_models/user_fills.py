from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone
from models.class_models.common import OrderSide


class OrderDirection(str, Enum):
    OPEN_LONG = "Open Long"
    OPEN_SHORT = "Open Short"
    CLOSE_LONG = "Close Long"
    CLOSE_SHORT = "Close Short"
    SELL = "Sell"
    BUY = "Buy"
    ADL = "Auto-Deleveraging"


class UserFillsModel(BaseModel):
    """
    User Fills Model

    Attributes:
        time (int): The timestamp of the fill in milliseconds.
        coin (str): The coin symbol.
        user (str): The user address.
        side (str): The order side: 'b' for buy, 'a' for sell.
        sz (float): The order size.
        price (float): The price at which the order was filled.
        fee (float): The fee associated with the fill.
        liquidated (bool): Whether the fill was due to liquidation.
        maker (bool): Whether the fill was a maker order.
        feeCoin (str): The coin in which the fee was charged.
        referrerRebate (float): The rebate given to the referrer, if any.
        orderId (int | None): The ID of the order associated with the fill, if available.
    """

    name: str = "UserFill"
    coin: str = Field(..., description="Coin symbol")
    px: float = Field(..., description="Price at which the order was filled")
    sz: float = Field(..., description="Order size")
    side: OrderSide = Field(..., description="Order side: 'b' for buy, 'a' for sell")
    time: int = Field(..., description="Timestamp in microseconds")
    startPosition: float = Field(..., description="Starting position before the fill")
    dir: OrderDirection = Field(..., description="Order direction")
    closedPnl: float = Field(..., description="Closed PnL from the fill")
    hash: str = Field(..., description="Transaction hash")
    oid: int | None = Field(None, description="Order ID")
    crossed: bool = Field(..., description="Whether the fill crossed the spread")
    fee: float = Field(..., description="Fee associated with the fill")
    tid: int = Field(..., description="Trade ID")
    feeToken: str = Field(..., description="Coin in which the fee was charged")
    twapId: int | None = Field(None, description="TWAP order ID, if applicable")

    @property
    def datetime(self):
        """returns the datetime object corresponding to the fill time."""
        return datetime.fromtimestamp(self.time / 1e6, tz=timezone.utc)
