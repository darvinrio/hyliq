from pydantic import BaseModel, Field, computed_field
from datetime import datetime, timezone
from models.class_models.common import OrderSide
from typing import Literal, Union


class DepositTxModel(BaseModel):
    """
    Deposit from Arbitrum
    """

    type: str = "deposit"
    usdc: float = Field(..., description="USDC amount deposited")


class WithdrawTxModel(BaseModel):
    """
    Withdraw to Arbitrum
    """

    type: str = "withdraw"
    usdc: float = Field(..., description="USDC amount withdrawn")
    nonce: int = Field(..., description="Withdrawal nonce")
    fee: float = Field(..., description="Withdrawal fee")


class VaultDepositTxModel(BaseModel):
    """
    Deposit to Vault
    """
    type: str = "vaultDeposit"
    vault: str = Field(..., description="Vault address")
    usdc: float = Field(..., description="USDC amount deposited to vault")


class VaultWithdrawTxModel(BaseModel):
    """
    Withdraw from Vault
    """
    type: str = "vaultWithdraw"
    vault: str = Field(..., description="Vault address")
    user: str = Field(..., description="User address")
    requestedUsd: float = Field(..., description="USDC amount requested for withdrawal")
    commission: float = Field(..., description="Commission fee")
    closingCost: float = Field(..., description="Closing cost")
    basis: float = Field(..., description="Basis amount")
    netWithdrawnUsd: float = Field(..., description="USDC amount withdrawn from vault")

class InternalTransferTxModel(BaseModel):
    """
    Internal transfer between users
    """

    type: str = "internalTransfer"
    usdc: float = Field(..., description="USDC amount transferred")
    user: str = Field(..., description="User address initiating the transfer")
    destination: str = Field(..., description="Destination user address")
    fee: float = Field(..., description="Transfer fee")


class AccountClassTransferTxModel(BaseModel):
    """
    Transfer between Spot and Perp accounts
    """

    type: str = "accountClassTransfer"
    usdc: float = Field(..., description="USDC amount transferred")
    toPerp: bool = Field(
        ...,
        description="True if transferring to Perp account, False if to Spot account",
    )


class SpotTransferTxModel(BaseModel):
    """
    Spot transfer between users
    """

    type: str = "spotTransfer"
    token: str = Field(..., description="Token being transferred")
    amount: float = Field(..., description="Amount of token transferred")
    usdcValue: float = Field(..., description="USDC value of the token transferred")
    user: str = Field(..., description="User address initiating the transfer")
    destination: str = Field(..., description="Destination user address")
    fee: float = Field(..., description="Transfer fee")
    nativeTokenFee: float = Field(..., description="Native token fee for the transfer")
    feeToken: str | None = Field(None, description="Token used to pay the fee")


class CStakingTransferTxModel(BaseModel):
    type: str = "cStakingTransfer"
    token: str = Field(..., description="Token being staked/unstaked")
    amount: float = Field(..., description="Amount of token staked/unstaked")
    isDeposit: bool = Field(
        ..., description="True if deposit (stake), False if withdrawal (unstake)"
    )


class AccountActivationGasTxModel(BaseModel):
    type: str = "accountActivationGas"
    amount: float = Field(..., description="Gas fee for account activation")
    token: str = Field(..., description="Token used to pay the gas fee")


LedgerUpdates = Union[
    DepositTxModel,
    WithdrawTxModel,
    VaultDepositTxModel,
    VaultWithdrawTxModel,
    InternalTransferTxModel,
    AccountClassTransferTxModel,
    SpotTransferTxModel,
    CStakingTransferTxModel,
    AccountActivationGasTxModel,
]


class TxModel(BaseModel):
    """
    User Ledger Update Model
    """

    time: int = Field(..., description="Timestamp in milliseconds")
    hash: str = Field(..., description="Transaction hash")
    delta: LedgerUpdates = Field(..., description="Ledger update details")

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.time / 1000, tz=timezone.utc)

    @computed_field
    @property
    def name(self) -> str:
        return self.delta.type + "Tx"
