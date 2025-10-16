from loguru import logger
from config import REFRESH
from loaders.portfolio import get_portfolio, combine_portfolios
import polars as pl

from loaders.twap import get_twap_history_dataframe
from loaders.user_fills import get_user_fills_dataframe
from loaders.user_funding import get_user_funding_dataframe
from loaders.user_ledger_updates import get_user_ledger_updates_dataframe
from viz.portfolio import visualize_portfolio

dnhype_short_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
dnhype_spot_eoa = "0xca36897cd0783a558f46407cd663d0f46d2f3386"


def plot_dnhype_portfolio():
    """Plot dnHYPE strategy portfolios."""

    dnhype_short_portfolio = get_portfolio(address=dnhype_short_eoa).filter(
        pl.col("period") == "allTime"
    )
    dnhype_spot_portfolio = get_portfolio(address=dnhype_spot_eoa).filter(
        pl.col("period") == "allTime"
    )

    # Combine the two portfolios
    combined_portfolio = combine_portfolios(
        [dnhype_short_portfolio, dnhype_spot_portfolio]
    )

    # logger.debug(f"Individual Short Portfolio:\n{dnhype_short_portfolio.tail()}")
    # logger.debug(f"Individual Spot Portfolio:\n{dnhype_spot_portfolio.tail()}")
    # logger.debug(f"Combined Portfolio:\n{combined_portfolio.tail()}")

    short_viz = visualize_portfolio(
        dnhype_short_portfolio,
        title=f"dnHYPE Short Portfolio - {dnhype_short_eoa}",
        show_account_value=False,
    )
    spot_viz = visualize_portfolio(
        dnhype_spot_portfolio,
        title=f"dnHYPE Spot Portfolio - {dnhype_spot_eoa}",
        show_account_value=False,
    )
    combined_viz = visualize_portfolio(
        combined_portfolio,
        title="Combined dnHYPE Strategy Portfolio",
        show_account_value=False,
    )

    viz = (
        (spot_viz & short_viz & combined_viz)
        # .resolve_scale(y="independent")
        .properties(title="DNHYPE Portfolio Overview")
    )
    viz.save("portfolio.html")

def get_dnhype_actions_df():
    eoas = [
        {"address": dnhype_short_eoa, "label": "DN Hype Short"},
        {"address": dnhype_spot_eoa, "label": "DN Hype Spot"},
    ]

    for eoa in eoas:
        addr = eoa["address"]
        label = eoa["label"]
        logger.info(f"Processing {label} - {addr}")
        filename_uid = f"{label.replace(' ','_').lower()}"

        twap_df = get_twap_history_dataframe(addr, use_cache=not REFRESH)
        twap_df.write_csv(f"debug/{filename_uid}_twap.csv")

        fills_df = get_user_fills_dataframe(addr, use_cache=not REFRESH)
        fills_df.write_csv(f"debug/{filename_uid}_fills.csv")

        funding_df = get_user_funding_dataframe(addr, use_cache=not REFRESH)
        funding_df.write_csv(f"debug/{filename_uid}_funding.csv")

        ledger_updates_df = get_user_ledger_updates_dataframe(addr, use_cache=not REFRESH)
        ledger_updates_df.write_csv(f"debug/{filename_uid}_ledger_updates.csv")
        
        twap_df.select([
            "coin",
            "side",
            # "executedNtl", # actual size executed
        ]).unique().write_csv(f"debug/unique/twap.csv")
        
        fills_df.select([
            "coin",
            "side",
            # "dir", 
            # "sz", # actual size executed
        ]).unique().write_csv(f"debug/unique/fills.csv")
        
        ledger_updates_df.select([
            "delta_type",
            "token",
            # "amount",
            "user",
            "destination",
            "toPerp",
            "isDeposit",
        ]).unique().write_csv(f"debug/unique/ledger_updates.csv")
        
        
        