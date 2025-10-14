from loguru import logger
from utils.portfolio import get_portfolio
import json
import polars as pl

from viz.portfolio import visualize_portfolio

dnhype_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
p = get_portfolio(address=dnhype_eoa)

spot_df = p.filter(pl.col("period") == "allTime")
perp_df = p.filter(pl.col("period") == "perpAllTime")
# print(json.dumps(p, indent=4))

spot_viz = visualize_portfolio(spot_df)
perp_viz = visualize_portfolio(perp_df)

viz = (
    (spot_viz & perp_viz)
    # .resolve_scale(y="independent")
    .properties(title="DNHYPE Portfolio Overview")
)
viz.save("portfolio.html")
