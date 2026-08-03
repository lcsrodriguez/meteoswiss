"""Logic to handle MeteoSwiss geo points"""

from io import StringIO

import httpx
import polars as pl

from meteoswiss_retriever.constants import (
    BASE_URL,
    LOCAL_FORECAST_COLLECTION_ID,
    REMOVED_LANGUAGES,
)


def query_geo_points(raise_errors: bool = True) -> pl.DataFrame:
    """
    Function to retrieve and return MeteoSwiss geo points
    (see docs: https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data?metadata=points)
    :param raise_errors: Raising errors if HTTP exception occurs
    :type raise_errors: bool
    :return: Polars DataFrame with geo points from MeteoSwiss
    :rtype: pl.DataFrame
    """
    r = httpx.get(
        url=f"{BASE_URL}/{LOCAL_FORECAST_COLLECTION_ID}/ogd-local-forecasting_meta_point.csv",
    )
    if raise_errors:
        r.raise_for_status()

    return pl.read_csv(StringIO(r.text), separator=";")


def clean_points(points: pl.DataFrame) -> pl.DataFrame:
    """
    Function to clean geo points dataframe
    :param points: Queried geo points
    :type points: pl.DataFrame
    :return: Cleaned geo points
    :rtype: pl.DataFrame
    """
    return points.drop([f"point_type_{lang}" for lang in REMOVED_LANGUAGES])
