import polars as pl

portfolio_period_enum = pl.Enum(
    [
        "perpAllTime",
        "perpMonth",
        "perpDay",
        "week",
        "perpWeek",
        "allTime",
        "month",
        "day",
    ]
)

portfolio_schema = pl.Schema(
    {
        "period": portfolio_period_enum,
        "timestamp": pl.Datetime("ms"),
        "account_value": pl.Float64,
        "pnl": pl.Float64,
        "vlm": pl.Float64,
    }
)
