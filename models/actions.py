import polars as pl

action_class_enum = pl.Enum([
    "VALIDATING",
    "DEPOSIT",
    "DUST",
    "WITHDRAW",
    "SPOT",
    "TRANSFER",
    "PERP",
])

actions_type_enum = pl.Enum([
    "Auto-Deleveraging",
    "InternalTransfer",
    "Open Short",
    "Sell",
    "Buy",
    "Withdraw",
    "Spot Dust Conversion",
    "Twap",
    "Deposit",
    "tokenDelegate",
    "Transfer",
    "order",
])

actions_schema = pl.Schema({
    "class": action_class_enum,
    "hash": pl.String,
    "time": pl.Datetime("ms"),
    "token": pl.String,
    "type": actions_type_enum,
    "amount": pl.Float64,
    "from": pl.String,
    "to": pl.String,
    "px": pl.Float64,
    "USDAmount": pl.Float64,
    "priority": pl.Int64,
    "fee": pl.Float64,
})