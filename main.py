from loguru import logger
import polars as pl

from loaders.actions import generate_positions
from loaders.explorer import get_user_details_dataframe
from loaders.twap import get_twap
from workflows.dn_hype import plot_dnhype

dnhype_short_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
dnhype_spot_eoa = "0xca36897cd0783a558f46407cd663d0f46d2f3386"

# plot_dnhype()

# hist_df, latest_df = generate_positions(dnhype_short_eoa)
# u = get_user_details_dataframe(dnhype_short_eoa)

# logger.debug(hist_df.tail())
# # logger.debug(d.select("class").unique())
# logger.debug(hist_df.select("class","type").unique().write_csv("debug/actions.csv"))
# # logger.debug(d.select("type").unique().to_series().to_list())

# hist_df.write_csv("debug/dnhype_short_hist.csv")
# latest_df.write_csv("debug/dnhype_short_latest.csv")

twap_df = get_twap(dnhype_short_eoa)

