"""Sample script to retrieve all available data (forecasts/measurements/weather alerts) for a given input postal code"""
# ruff: noqa: E402

from meteoswiss_retriever.utils.logs import setup_logger

setup_logger()

from typing import Dict

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
    # point_geo = postal_code_details.select("lon", "lat").to_dict(as_series=False)
    # point_lon, point_lat = (point_geo["lon"][0], point_geo["lat"][0])

    point_loc: Location = from_series_to_location_obj(postal_code_details)

    # Retrieving forecasts
    links = query_local_forecast_asset_links()
    forecasts_data = collect_assets_data(links)

    # Getting forecasts for respective
    forecasts = get_forecast_data(forecasts_data, point_loc, parameters=params)

    res["data"]["forecasts"] = forecasts
    # Retrieving measurements

    # Retrieving weather alerts
    print()

    return res


# TODO: Set up scheduler + service to download in background
# + support for cron monitoring
