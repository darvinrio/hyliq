from loguru import logger
from utils.portfolio import get_portfolio, combine_portfolios
import json
import polars as pl

from viz.portfolio import visualize_portfolio

dnhype_short_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
dnhype_spot_eoa = "0xca36897cd0783a558f46407cd663d0f46d2f3386"

dnhype_short_portfolio = get_portfolio(address=dnhype_short_eoa).filter(
    pl.col("period") == "allTime"
)
dnhype_spot_portfolio = get_portfolio(address=dnhype_spot_eoa).filter(
    pl.col("period") == "allTime"
)

# Combine the two portfolios
combined_portfolio = combine_portfolios([dnhype_short_portfolio, dnhype_spot_portfolio])

logger.debug(f"Individual Short Portfolio:\n{dnhype_short_portfolio.tail()}")
logger.debug(f"Individual Spot Portfolio:\n{dnhype_spot_portfolio.tail()}")
logger.debug(f"Combined Portfolio:\n{combined_portfolio.tail()}")

short_viz = visualize_portfolio(dnhype_short_portfolio, title=f"dnHYPE Short Portfolio - {dnhype_short_eoa}")
spot_viz = visualize_portfolio(dnhype_spot_portfolio, title=f"dnHYPE Spot Portfolio - {dnhype_spot_eoa}")
combined_viz = visualize_portfolio(combined_portfolio, title="Combined dnHYPE Strategy Portfolio")

viz = (
    (spot_viz & short_viz & combined_viz)
    # .resolve_scale(y="independent")
    .properties(title="DNHYPE Portfolio Overview")
)
viz.save("portfolio.html")
