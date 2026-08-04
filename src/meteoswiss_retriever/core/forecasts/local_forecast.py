"""Logic to handle local forecast data download/management"""

from datetime import date, datetime
from typing import Any, Dict, List

import httpx

from meteoswiss_retriever.constants import BASE_URL, LOCAL_FORECAST_COLLECTION_ID
from meteoswiss_retriever.utils.date import (
    get_date_from_str,
    get_datetime_from_iso_str,
    get_datetime_from_str,
)

# These files are updated every hour
# Items: https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-local-forecasting/items
# For each item (= 1 day), there are multiple assets to be downloaded


def query_available_items(raise_errors: bool = True) -> Any:
    """
    Function to query and retrieve all items available (days) in the local forecast collection
    (see: https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-local-forecasting/items)
    :param raise_errors: Boolean to raise if error occurs
    :type raise_errors: bool
    :return: List of items
    :rtype: List[Dict[str, Any]]
    """

    r = httpx.get(
        url=f"{BASE_URL}/api/stac/v1/collections/{LOCAL_FORECAST_COLLECTION_ID}/items",
    )
    if raise_errors:
        r.raise_for_status()
    data = r.json()

    latest_update = get_datetime_from_iso_str(data["timeStamp"])
    print(f"Latest update of the collection: {latest_update}")
    return data["features"]


def get_available_forecast_days(
    features: List[Dict[str, Any]],
) -> Dict[date, Dict[str, Any]]:
    """
    Function to collect available forecast days
    :param features: List of features (previously collected)
    :type features: List[Dict[str, Any]]
    :return: Dict with available forecast days + timestamp details
    :rtype: Dict[date, Dict[str, Any]]
    """
    return {
        get_date_from_str(f["id"].replace("-ch", "")): {
            k: v for k, v in f["properties"].items() if k != "title"
        }
        for f in features
    }


def query_local_forecast_asset_links(  # query_local_forecast_item
    day: date | None = None,
    raise_errors: bool = True,
    # forecast_inception_hour: str | int | None = None,  # To force instead of latest_update_dt
    # params_list: List[str] | None = None, # To pre-select specific parameters
) -> Dict[str, Dict[str, Any]]:
    """
    Function to query and retrieve the list of URLs to be later queried
    :param day: Forecast day
    :type day: str | None
    :param raise_errors: Boolean to raise if error occurs
    :type raise_errors: bool
    :return: Dict with valid forecast data link for each parameter
    :rtype: Dict[str, Dict[str, Any]]
    """

    if day is None:
        day = date.today()

    day_str: str = f"{day.strftime('%Y%m%d')}-ch"

    # https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-local-forecasting/items/20260803-ch
    r = httpx.get(
        url=f"{BASE_URL}/api/stac/v1/collections/{LOCAL_FORECAST_COLLECTION_ID}/items/{day_str}",
    )
    if raise_errors:
        r.raise_for_status()

    data = r.json()
    assets = data["assets"]

    # Retrieving last update datetime
    latest_update_dt = _get_latest_forecast_available_hour(assets)
    print(latest_update_dt)

    # Checking
    print("Available forecast hours")
    print(_get_forecast_available_hours(assets))

    # Collecting links
    links: Dict = {}
    for asset_name, asset_details in assets.items():
        # Getting current asset hour
        asset_dt_hour: datetime = get_datetime_from_str(asset_name.split(".")[2])

        # Only selecting latest forecast data ('fresh data')
        if asset_dt_hour == latest_update_dt:
            param_name: str = str(asset_name.split(".")[3])

            links[param_name] = {
                "link": asset_details["href"],
            }

    return links


def _get_latest_forecast_available_hour(
    assets: Dict[str, Dict[str, str | int]],
) -> datetime:
    """
    Function to get the latest available forecast hour from retrieved assets
    :param assets: Assets
    :type assets: Dict[str, Dict[str, str | int]]
    :return: Datetime object
    :rtype: datetime
    """
    latest_update_dt = sorted({k.split(".")[2] for k in assets.keys()})[-1]
    return get_datetime_from_str(latest_update_dt)


def _get_forecast_available_hours(
    assets: Dict[str, Dict[str, str | int]],
) -> List[datetime]:
    """
    Function to get all forecast available hours in the selected day (from input assets)
    :param assets: Assets
    :type assets: Dict[str, Dict[str, str | int]]
    :return: List of available forecast hours (list of datetime objects)
    :rtype: List[datetime]
    """
    return [
        get_datetime_from_str(h)
        for h in sorted({k.split(".")[2] for k in assets.keys()})
    ]
