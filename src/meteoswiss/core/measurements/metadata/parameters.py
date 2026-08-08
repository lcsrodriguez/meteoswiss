"""Sub-module for MeteoSwiss ground measurement parameters"""

from io import StringIO

import httpx
import polars as pl

from meteoswiss.constants import (
    BASE_URL,
    ENCODING_FORMAT,
    GROUND_MEASUREMENTS_COLLECTION_ID,
    REMOVED_LANGUAGES,
)
from meteoswiss.utils.logs import get_logger

logger = get_logger(__name__)


def query_parameters(raise_errors: bool = True) -> pl.DataFrame:
    """
    Function to retrieve and return MeteoSwiss ground-based measurement parameters
    (see docs: https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations?metadata=parameters)
    :param raise_errors: Raising errors if HTTP exception occurs
    :type raise_errors: bool
    :return: Polars DataFrame with parameters from MeteoSwiss
    :rtype: pl.DataFrame
    """

    # link: https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/ogd-smn_meta_parameters.csv
    logger.info("Querying MeteoSwiss local forecast parameters (metadata)")
    r = httpx.get(
        url=f"{BASE_URL}/{GROUND_MEASUREMENTS_COLLECTION_ID}/ogd-smn_meta_parameters.csv",
    )
    if raise_errors:
        r.raise_for_status()

    return pl.read_csv(StringIO(r.content.decode(ENCODING_FORMAT)), separator=";")


def clean_parameters(parameters: pl.DataFrame) -> pl.DataFrame:
    """
    Function to clean queried parameters
    :param parameters: Queried parameters
    :type parameters: pl.DataFrame
    :return: Cleaned parameters
    :rtype: pl.DataFrame
    """
    return parameters.drop(
        [f"parameter_description_{lang}" for lang in REMOVED_LANGUAGES]
        + [f"parameter_group_{lang}" for lang in REMOVED_LANGUAGES]
    )
