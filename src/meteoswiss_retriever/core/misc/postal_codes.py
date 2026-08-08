"""Sub-module to retrieve postal codes"""

from pathlib import Path

import polars as pl

from meteoswiss_retriever.constants import CSV_SEPARATOR, POSTAL_CODES_CSV
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)


def get_postal_codes(filename: str | Path | None = POSTAL_CODES_CSV) -> pl.DataFrame:
    """
    Function to retrieve postal codes
    :param filename: Data filename
    :type filename: str | Path | None
    :return: DataFrame with postal codes
    :rtype: pl.DataFrame
    """
    if filename is None:
        logger.error("No filename provided")
    elif isinstance(filename, str):
        filename = Path(filename)

    postal_codes = pl.read_csv(filename, separator=CSV_SEPARATOR)

    return postal_codes.select(
        # pl.col("Ortschaftsname"),
        pl.col("PLZ4"),
        pl.col("Gemeindename"),
        pl.col("Kantonskürzel"),
    ).rename(
        {
            # "Ortschaftsname": "",
            "PLZ4": "postal_code",
            "Gemeindename": "city",
            "Kantonskürzel": "canton",
        }
    )
