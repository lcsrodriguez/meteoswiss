"""Logic to handle local forecast data download/management"""

from datetime import date, datetime
from io import StringIO
from typing import Any, Dict, List

import httpx
import polars as pl

from meteoswiss_retriever.constants import (
    BASE_URL,
    ENCODING_FORMAT,
    LOCAL_FORECAST_COLLECTION_ID,
)
from meteoswiss_retriever.utils.date import (
    get_date_from_str,
    get_datetime_from_iso_str,
    get_datetime_from_str,
)
from meteoswiss_retriever.utils.export import save_df

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
    # force_forecast_hour: str | int | None = None,  # To force instead of latest_update_dt
    force_params_list: List[str] | None = None,  # To pre-select specific parameters
) -> Dict[str, Dict[str, Any]]:
    """
    Function to query and retrieve the list of URLs to be later queried
    :param day: Forecast day
    :type day: str | None
    :param raise_errors: Boolean to raise if error occurs
    :type raise_errors: bool
    :param force_params_list: List of parameters to enforce URL collection (defaults to all parameters)
    :type force_params_list: List[str] | None
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
        # Getting parameter/field/asset name
        param_name: str = str(asset_name.split(".")[3])

        # Enforcing specific parameters if needed
        if force_params_list is not None:
            if param_name not in force_params_list:
                continue

        # Getting current asset hour
        asset_dt_hour: datetime = get_datetime_from_str(asset_name.split(".")[2])

        # Only selecting latest forecast data ('fresh data')
        if asset_dt_hour == latest_update_dt:
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


def collect_assets_data(
    links: Dict[str, Dict[str, str]], raise_errors: bool = True, save: bool = True
) -> Dict[str, pl.DataFrame]:
    """
    Function to collect data for all assets (HTTP requests)
    :param links: Dictionary with available forecast links filtered by asset
    :type links: Dict[str, Dict[str, str]]
    :param raise_errors: Boolean to raise if HTTP error occurs
    :type raise_errors: bool
    :param save: On-disk save
    :type save: bool
    :return: Dict of forecast dataframes
    :rtype: Dict[str, pl.DataFrame]
    """

    data: Dict[str, pl.DataFrame] = {}

    with httpx.Client() as client:
        for asset_name, asset_details in links.items():
            print(f"Starting asset {asset_name}")
            # Performing HTTP request
            req = client.get(asset_details["link"])
            if raise_errors:
                req.raise_for_status()

            # Reading CSV payload
            d_ = pl.read_csv(
                StringIO(req.content.decode(ENCODING_FORMAT)), separator=";"
            )

            if save:
                # Saving CSV on-disk
                save_df(df=d_, path=f"data/forecasts/dl/{asset_name}.csv")
            data[asset_name] = d_
            print(f"Finishing asset {asset_name}")

    return data


def read_local_data(params: List[str]) -> Dict[str, pl.DataFrame]:
    """
    Function to read local data (already-collected asset data)
    :param params: List of parameter names
    :type params: List[str]
    :return: Dict of data by parameter name
    :rtype: Dict[str, pl.DataFrame]
    """
    data: Dict[str, pl.DataFrame] = {param: pl.DataFrame() for param in params}

    for param in params:
        print(f"Reading local data for param: {param}")
        data[param] = pl.read_csv(f"data/forecasts/dl/{param}.csv", separator=";")

    return data
