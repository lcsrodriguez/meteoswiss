"""Logic to handle local forecast data download/management"""

from typing import Any, Dict

import httpx

from meteoswiss_retriever.constants import (
    BASE_URL,
    GROUND_MEASUREMENTS_COLLECTION_ID,
)
from meteoswiss_retriever.utils.date import (
    get_datetime_from_iso_str,
)
from meteoswiss_retriever.utils.logs import get_logger

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
