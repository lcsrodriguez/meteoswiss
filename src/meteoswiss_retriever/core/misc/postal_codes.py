"""Sub-module to retrieve postal codes"""

from pathlib import Path
from typing import Dict, List

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


def check_postal_code(codes: pl.DataFrame, postal_code: int | None = None) -> bool:
    """
    Function to check if an input postal code is valid (Switzerland)
    :param codes: DataFrame with postal codes details
    :type codes: pl.DataFrame
    :param postal_code: Input postal code
    :type postal_code: int | None
    :return: True if postal code is valid, False otherwise
    :rtype: bool
    """
    if postal_code is None:
        return False

    if codes.filter(pl.col("postal_code") == postal_code).is_empty():
        return False
    return True


def get_postal_code_details(
    codes: pl.DataFrame, postal_code: int | None = None
) -> Dict[str, List[str | int] | str | int]:
    """
    Function to get details of postal code (city name, canton)
    :param codes: DataFrame with postal codes details
    :type codes: pl.DataFrame
    :param postal_code: Input postal code
    :type postal_code: int | None
    :return: Dict with details of postal code
    :rtype: Dict[str, List[str | int] | str | int]
    """
    if postal_code is None:
        return {}
    return codes.filter(pl.col("postal_code") == postal_code).to_dict(as_series=False)
