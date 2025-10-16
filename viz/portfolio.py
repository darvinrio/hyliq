import altair as alt
import polars as pl
from loguru import logger
from config import chart_width, chart_height
from models.df_models.portfolio import portfolio_period_enum, portfolio_schema
from utils.num import format_number


def visualize_portfolio(
    df: pl.DataFrame,
    title: str = None,
    show_pnl: bool = True,
    show_account_value: bool = True,
) -> alt.Chart:

    if df.schema != portfolio_schema:
        logger.error(
            f"DataFrame schema does not match expected portfolio schema. \n received schema: {df.schema} \n expected schema: {portfolio_schema}"
        )
        raise ValueError("Invalid DataFrame schema")

    if not show_pnl and not show_account_value:
        raise ValueError("At least one metric (PNL or Account Value) must be shown")

    # Transform data to long format for proper legend
    columns_to_select = ["timestamp"]
    metrics_to_show = []

    if show_account_value:
        columns_to_select.append(pl.col("account_value").alias("Account Value"))
        metrics_to_show.append("Account Value")

    if show_pnl:
        columns_to_select.append(pl.col("pnl").alias("PNL"))
        metrics_to_show.append("PNL")

    df_long = df.select(columns_to_select).unpivot(
        index=["timestamp"],
        on=metrics_to_show,
        variable_name="metric",
        value_name="value",
    )

    chart = (
        alt.Chart(df_long)
        .mark_line()
        .encode(
            x=alt.X("timestamp", title="Timestamp"),
            y=alt.Y(
                "value",
                title="Value (USD)",
                axis=alt.Axis(
                    format="~s",  # SI prefix formatting (K, M, B)
                    labelExpr="datum.value >= 1e9 ? format(datum.value / 1e9, '.1f') + 'B' : datum.value >= 1e6 ? format(datum.value / 1e6, '.1f') + 'M' : datum.value >= 1e3 ? format(datum.value / 1e3, '.1f') + 'K' : format(datum.value, '.0f')",
                ),
            ),
            color=alt.Color(
                "metric:N",
                title="Metrics",
                scale=alt.Scale(
                    domain=metrics_to_show,
                    range=["blue", "orange"][: len(metrics_to_show)],
                ),
            ),
            tooltip=[
                "timestamp",
                "metric",
                alt.Tooltip("value:Q", title="Value (USD)", format="~s"),
            ],
        )
    ).properties(
        title=title if title else "Portfolio Overview",
        width=chart_width,
        height=chart_height,
    )

    return chart
