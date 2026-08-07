"""Sample script to retrieve all available data (forecasts/measurements/weather alerts) for a given input postal code"""
# ruff: noqa: E402

from meteoswiss_retriever.utils.logs import setup_logger

setup_logger()

from typing import Dict

import polars as pl

from meteoswiss_retriever.core.forecasts.local_forecast import (
    collect_assets_data,
    get_forecast_data,
    query_local_forecast_asset_links,
)
from meteoswiss_retriever.core.forecasts.metadata.parameters import (
    clean_parameters,
    query_parameters,
)
from meteoswiss_retriever.core.forecasts.metadata.points import (
    Location,
    clean_points,
    from_series_to_location_obj,
    get_point_by_postal_code,
    query_geo_points,
)
from meteoswiss_retriever.core.measurements.ground_measurements import (
    collect_assets_data as collect_measurements_data,
)
from meteoswiss_retriever.core.measurements.ground_measurements import (
    query_measurements_asset_links,
)
from meteoswiss_retriever.core.measurements.metadata.stations import (
    clean_stations,
    query_stations,
)
from meteoswiss_retriever.utils.geo import computer_haversine_dist
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)


def postal_code_retriever(postal_code: int | None = None) -> Dict:
    """
    Function to retrieve all available data (forecasts/measurements/weather alerts) for a given input postal code
    :param postal_code: Postal code (int)
    :type postal_code: int | None
    :return: Dict of data
    :rtype: Dict
    """

    if postal_code is None:
        logger.error("No postal code provided")
        return {}

    # Check postal code
    # TODO: API for postal code (check data.admin.ch)

    res: Dict = {"data": {}}

    # Get points
    points = clean_points(query_geo_points())

    # Getting parameters
    params = clean_parameters(query_parameters())

    # Getting point corresponding to postal code
    postal_code_details = get_point_by_postal_code(data=points, postal_code=postal_code)

    # Getting geo details from given postal code
    point_geo = postal_code_details.select("lon", "lat").to_dict(as_series=False)
    point_lon, point_lat = (point_geo["lon"][0], point_geo["lat"][0])

    point_loc: Location = from_series_to_location_obj(postal_code_details)

    # Retrieving forecasts
    logger.info("Retrieving forecasts...")
    links = query_local_forecast_asset_links()
    forecasts_data = collect_assets_data(links, save=False)

    # Getting forecasts for respective
    forecasts = get_forecast_data(forecasts_data, point_loc, parameters=params)

    res["data"]["forecasts"] = forecasts

    # Retrieving measurements
    logger.info("Retrieving measurements...")

    # Getting stations
    stations = clean_stations(query_stations())

    # Getting distance ranking (nearest to furthest) from postal code point
    stations_ranked = (
        stations.with_columns(
            distance_km=computer_haversine_dist(
                point_lon, point_lat, pl.col("lon"), pl.col("lat")
            )
        ).sort("distance_km")
    ).select(
        "station_abbr", "station_name", "station_canton", "lon", "lat", "distance_km"
    )

    # Adding numeric ranking
    stations_ranked = stations_ranked.with_columns(rank=pl.int_range(1, pl.len() + 1))

    # nearest_station_from_postal_code = stations_ranked.head(1)
    nearest_station_from_postal_code = stations_ranked.filter(pl.col("rank") == 1)

    nearest_station_abbr = str(
        nearest_station_from_postal_code.select(pl.col("station_abbr")).to_dict(
            as_series=False
        )["station_abbr"][0]
    ).lower()

    assets_links = query_measurements_asset_links(station_abbr=nearest_station_abbr)

    measurements = collect_measurements_data(assets_links, save=False)
    res["data"]["measurements"] = measurements

    # Retrieving weather alerts
    print()

    return res


# TODO: Set up scheduler + service to download in background
# + support for cron monitoring

postal_code_retriever(postal_code=1012)
