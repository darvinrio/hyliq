from turtle import color, width
import altair as alt
import polars as pl
from loguru import logger
from config import chart_width, chart_height


def visualize_portfolio(df: pl.DataFrame) -> alt.Chart:
    expected_portfolio_schema = pl.Schema(
        {
            "period": pl.String,
            "timestamp": pl.Datetime("ms"),
            "account_value": pl.Float64,
            "pnl": pl.Float64,
            "vlm": pl.Float64,
        }
    )

    if df.schema != expected_portfolio_schema:
        logger.error(
            f"DataFrame schema does not match expected portfolio schema. \n received schema: {df.schema} \n expected schema: {expected_portfolio_schema}"
        )
        raise ValueError("Invalid DataFrame schema")

    acc_val = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("timestamp", title="Timestamp"),
            y=alt.Y("account_value", title="Account Value (USD)"),
            color=alt.value("blue"),
            tooltip=["timestamp", "account_value"],
        )
    )
    pnl = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("timestamp", title="Timestamp"),
            y=alt.Y("pnl", title="PNL (USD)"),
            color=alt.value("orange"),
            tooltip=["timestamp", "pnl"],
        )
    )

    chart = (acc_val + pnl).properties(
        title="Portfolio Account Value Over Time",
        width=chart_width,
        height=chart_height,
    )

    return chart
