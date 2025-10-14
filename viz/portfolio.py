import altair as alt
import polars as pl
from loguru import logger
from config import chart_width, chart_height


def visualize_portfolio(df: pl.DataFrame, title:str = None) -> alt.Chart:
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

    # Transform data to long format for proper legend
    df_long = df.select([
        "timestamp",
        pl.col("account_value").alias("Account Value"),
        pl.col("pnl").alias("PNL")
    ]).unpivot(
        index=["timestamp"],
        on=["Account Value", "PNL"],
        variable_name="metric",
        value_name="value"
    )
    
    chart = (
        alt.Chart(df_long)
        .mark_line()
        .encode(
            x=alt.X("timestamp", title="Timestamp"),
            y=alt.Y("value", title="Value (USD)"),
            color=alt.Color(
                "metric:N", 
                title="Metrics",
                scale=alt.Scale(
                    domain=["Account Value", "PNL"],
                    range=["blue", "orange"]
                )
            ),
            tooltip=["timestamp", "metric", "value"],
        )
    ).properties(
        title=title if title else "Portfolio Overview",
        width=chart_width,
        height=chart_height,
    )

    return chart
