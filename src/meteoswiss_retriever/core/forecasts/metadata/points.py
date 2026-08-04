"""Logic to handle MeteoSwiss geo points"""

from io import StringIO
from typing import NamedTuple

import httpx
import polars as pl

from meteoswiss_retriever.constants import (
    BASE_URL,
    ENCODING_FORMAT,
    LOCAL_FORECAST_COLLECTION_ID,
    REMOVED_LANGUAGES,
)


class Location(NamedTuple):
    """
    Location named tuple
    (point_id, point_type_id) represents a unique point in the dataset
    """

    point_id: int
    point_type_id: int


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

    return pl.read_csv(StringIO(r.content.decode(ENCODING_FORMAT)), separator=";")


def clean_points(points: pl.DataFrame) -> pl.DataFrame:
    """
    Function to clean geo points dataframe
    :param points: Queried geo points
    :type points: pl.DataFrame
    :return: Cleaned geo points
    :rtype: pl.DataFrame
    """
    return points.drop([f"point_type_{lang}" for lang in REMOVED_LANGUAGES])


def get_unique_point(
    data: pl.DataFrame, point_id: int, point_type_id: int
) -> pl.DataFrame:
    """
    Function to get unique geo point from geo point_id and point_type_id
    :param data: Polars DataFrame
    :type data: pl.DataFrame
    :param point_id: Point ID
    :type point_id: int
    :param point_type_id: Point type ID
    :type point_type_id: int
    :return: Unique geo point details from metadata points
    :rtype: pl.DataFrame
    """
    return data.filter(
        (data["point_id"] == str(point_id))
        & (data["point_type_id"] == str(point_type_id))
    )


def get_point_by_postal_code(
    data: pl.DataFrame, postal_code: int | str | None = None
) -> pl.DataFrame:
    """
    Function to get specific geo point by postal code
    :param data: Polars DataFrame
    :type data: pl.DataFrame
    :param postal_code: Postal code (integer)
    :type postal_code: int | str | None
    :return: Unique geo point details from metadata points
    :rtype: pl.DataFrame
    """
    if postal_code is None:
        return pl.DataFrame()
    return data.filter((data["postal_code"] == str(postal_code)))


def from_series_to_location_obj(data: pl.DataFrame) -> Location:
    """
    Function to transform a Polars Series (one line from the metadata points) to a `Location` object (named tuple)
    :param data: Polars Series (one line from the metadata points)
    :type data: pl.DataFrame
    :return: Location object
    :rtype: Location
    """
    try:
        d = {
            k: v[0]
            for k, v in data.select("point_id", "point_type_id")
            .to_dict(as_series=False)
            .items()
        }
        return Location(**d)
    except IndexError:
        return Location(-1, -1)
