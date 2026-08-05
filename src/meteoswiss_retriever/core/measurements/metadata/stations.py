"""Logic to handle MeteoSwiss geo points"""

from io import StringIO

import httpx
import polars as pl

from meteoswiss_retriever.constants import (
    BASE_URL,
    ENCODING_FORMAT,
    GROUND_MEASUREMENTS_COLLECTION_ID,
    REMOVED_LANGUAGES,
)
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)


def query_stations(raise_errors: bool = True) -> pl.DataFrame:
    """
    Function to retrieve and return MeteoSwiss ground measurement stations
    (see docs: https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations?metadata=stations)
    :param raise_errors: Raising errors if HTTP exception occurs
    :type raise_errors: bool
    :return: Polars DataFrame with geo points from MeteoSwiss
    :rtype: pl.DataFrame
    """

    logger.info("Querying MeteoSwiss local forecast parameters (metadata)")

    # link: https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/ogd-smn_meta_stations.csv

    r = httpx.get(
        url=f"{BASE_URL}/{GROUND_MEASUREMENTS_COLLECTION_ID}/ogd-smn_meta_stations.csv",
    )
    if raise_errors:
        r.raise_for_status()

    return pl.read_csv(StringIO(r.content.decode(ENCODING_FORMAT)), separator=";")


def clean_stations(points: pl.DataFrame) -> pl.DataFrame:
    """
    Function to clean stations dataframe
    :param points: Queried geo points
    :type points: pl.DataFrame
    :return: Cleaned geo points
    :rtype: pl.DataFrame
    """
    return points.drop(
        [f"station_type_{lang}" for lang in REMOVED_LANGUAGES]
        + [f"station_exposition_{lang}" for lang in REMOVED_LANGUAGES]
        + [f"station_url_{lang}" for lang in REMOVED_LANGUAGES]
    ).rename(
        {"station_coordinates_wgs84_lat": "lat", "station_coordinates_wgs84_lon": "lon"}
    )
