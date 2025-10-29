from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from models.class_models.common import OrderSide


class OrderStatus(str, Enum):
    OPEN = "open"
    FILLED = "filled"
    CANCELED = "canceled"
    TERMINATED = "terminated"
    REJECTED = "minTradeNtlRejected"


class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"


class TimeInForce(str, Enum):
    GTC = "Gtc"  # Good Till Canceled
    FRONTEND_MARKET = "FrontendMarket"


class TriggerCondition(str, Enum):
    NA = "N/A"


class HistoricalOrderModel(BaseModel):
    """
    Historical Order Model

    Attributes:
        coin (str): The coin symbol.
        side (OrderSide): The order side: 'b' for buy, 'a' for sell.
        limitPx (float): The limit price of the order.
        sz (float): The current remaining size of the order.
        oid (int): The order ID.
        timestamp (int): The order creation timestamp.
        triggerCondition (str): The trigger condition.
        isTrigger (bool): Whether the order is a trigger order.
        triggerPx (float): The trigger price.
        isPositionTpsl (bool): Whether the order is a take-profit/stop-loss order.
        reduceOnly (bool): Whether the order is reduce-only.
        orderType (OrderType): The type of order (Market, Limit).
        origSz (float): The original order size.
        tif (TimeInForce): Time in force specification.
        cloid (str | None): Client order ID.
        status (OrderStatus): The current status of the order.
        statusTimestamp (int): The timestamp when the status was last updated.
    """

    name: str = "HistoricalOrder"
    coin: str = Field(..., description="Coin symbol")
    side: OrderSide = Field(..., description="Order side: 'b' for buy, 'a' for sell")
    limitPx: float = Field(..., description="Limit price")
    sz: float = Field(..., description="Current remaining size")
    oid: int = Field(..., description="Order ID")
    timestamp: int = Field(..., description="Order creation timestamp")
    triggerCondition: str = Field(..., description="Trigger condition")
    isTrigger: bool = Field(..., description="Whether it's a trigger order")
    triggerPx: float = Field(..., description="Trigger price")
    isPositionTpsl: bool = Field(..., description="Whether it's a TP/SL order")
    reduceOnly: bool = Field(..., description="Whether it's reduce-only")
    orderType: str = Field(..., description="Order type")
    origSz: float = Field(..., description="Original order size")
    tif: str = Field(..., description="Time in force")
    cloid: str | None = Field(None, description="Client order ID")
    status: OrderStatus = Field(..., description="Order status")
    statusTimestamp: int = Field(..., description="Status update timestamp")

    @property
    def datetime(self):
        """Convert timestamp to datetime object"""
        return datetime.fromtimestamp(self.timestamp / 1000, tz=timezone.utc)
    
    @property
    def status_datetime(self):
        """Convert status timestamp to datetime object"""
        return datetime.fromtimestamp(self.statusTimestamp / 1000, tz=timezone.utc)
    
    @property
    def is_buy(self) -> bool:
        """Check if this is a buy order"""
        return self.side == OrderSide.BUY
    
    @property
    def is_sell(self) -> bool:
        """Check if this is a sell order"""
        return self.side == OrderSide.SELL
    
    @property
    def is_filled(self) -> bool:
        """Check if the order is completely filled"""
        return self.status == OrderStatus.FILLED
    
    @property
    def filled_amount(self) -> float:
        """Calculate the filled amount"""
        return self.origSz - self.sz