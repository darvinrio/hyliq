from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Literal, Union


class UpdateLeverageModel(BaseModel):
    """
    User Update Leverage Model
    """

    name: str = "updateLeverage"
    time: int = Field(..., description="Timestamp in milliseconds")
    user: str = Field(..., description="User address")
    asset: int = Field(..., description="Asset ID")
    isCross: bool = Field(..., description="Whether the position is cross margin")
    leverage: float = Field(..., description="Leverage value")
    block: int = Field(..., description="Block number")
    hash: str = Field(..., description="Transaction hash")
    error: Union[str, None] = Field(None, description="Error message if any")

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.time / 1000, tz=timezone.utc)
