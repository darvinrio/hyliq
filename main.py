from loguru import logger
import polars as pl

from loaders.actions import get_actions

dnhype_short_eoa = "0x1Da7920cA7f9ee28D481BC439dccfED09F52a237"
dnhype_spot_eoa = "0xca36897cd0783a558f46407cd663d0f46d2f3386"

d = get_actions(dnhype_short_eoa)

logger.debug(d.tail())
