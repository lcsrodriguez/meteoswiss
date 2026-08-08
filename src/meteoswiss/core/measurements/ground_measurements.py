"""Logic to handle local forecast data download/management"""

from io import StringIO
from typing import Any, Dict

import httpx
import polars as pl

from meteoswiss.constants import (
    BASE_URL,
    ENCODING_FORMAT,
    GROUND_MEASUREMENTS_COLLECTION_ID,
)
from meteoswiss.utils.date import (
    get_datetime_from_iso_str,
)
from meteoswiss.utils.export import save_df
from meteoswiss.utils.logs import get_logger

logger = get_logger(__name__)

# These files are updated every hour
# Items: https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn/items
# For each item (= 1 day), there are multiple assets to be downloaded


def query_available_items(raise_errors: bool = True) -> Any:
    """
    Function to query and retrieve all items available (days) in the ground measurements collection
    (see: https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn/items)
    :param raise_errors: Boolean to raise if error occurs
    :type raise_errors: bool
    :return: List of items
    :rtype: List[Dict[str, Any]]
    """

    r = httpx.get(
        url=f"{BASE_URL}/api/stac/v1/collections/{GROUND_MEASUREMENTS_COLLECTION_ID}/items",
    )
    if raise_errors:
        r.raise_for_status()
    data = r.json()

    latest_update = get_datetime_from_iso_str(data["timeStamp"])
    logger.info(f"Latest update of the collection: {latest_update}")
    return data["features"]


# := query_measurements_asset_links // get_available_assets_per_station
def query_measurements_asset_links(
    station_abbr: str | None = None, raise_errors: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Function to query and return list of assets for a given station abbreviation
    :param station_abbr: Station abbreviation
    :type station_abbr: str | None
    :param raise_errors: Boolean to raise if HTTP error occurs
    :type raise_errors: bool
    :return: List of assets
    :rtype: Dict[str, Dict[str, Any]]
    """

    # link: https://data.geo.admin.ch/api/stac/v0.9/collections/ch.meteoschweiz.ogd-smn/items/puy

    if station_abbr is None:
        logger.error("Station abbreviation is not provided")
        return {}

    r = httpx.get(
        url=f"{BASE_URL}/api/stac/v1/collections/{GROUND_MEASUREMENTS_COLLECTION_ID}/items/{station_abbr.lower()}",
    )
    if raise_errors:
        r.raise_for_status()

    data = r.json()
    assets = data["assets"]

    # Collecting links
    links: Dict = {}
    for asset_name, asset_details in assets.items():
        # Getting parameter/field/asset name
        param_name: str = str(asset_name.split(".")[0])

        links[param_name] = {
            "link": asset_details["href"],
        }
    return links  # return assets


def collect_assets_data(
    links: Dict[str, Dict[str, str]], raise_errors: bool = True, save: bool = True
) -> Dict[str, pl.DataFrame]:
    """
    Function to collect data for all assets (HTTP requests)
    :param links: Dictionary with available measurements links filtered by asset
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
            logger.info(f"Starting asset {asset_name}")
            # Performing HTTP request
            req = client.get(asset_details["link"])
            if raise_errors:
                req.raise_for_status()

            # Reading CSV payload
            d_ = pl.read_csv(
                StringIO(req.content.decode(ENCODING_FORMAT)),
                separator=";",
                ignore_errors=True,
            )
            d_ = process_asset_df(d_)

            if save:
                # Saving CSV on-disk
                save_df(df=d_, path=f"data/measurements/dl/{asset_name}.csv")
            data[asset_name] = d_
            logger.info(f"Finishing asset {asset_name}")

    return data


def process_asset_df(data: pl.DataFrame) -> pl.DataFrame:
    """
    Function to process an asset dataframe
    :param data: Asset dataframe
    :type data: pl.DataFrame
    :return: Clean dataframe
    :rtype: pl.DataFrame
    """
    # data["Date"] = data["Date"].cast(pl.Datetime) # not working

    # Casting datetime + converting to correct tz
    data = data.with_columns(
        pl.col("reference_timestamp")
        .cast(pl.Utf8)
        .str.strptime(pl.Datetime, format="%d.%m.%Y %H:%M")
        .dt.replace_time_zone("UTC")
        .dt.convert_time_zone("Europe/Zurich")
    )
    return data
