"""Logic to handle local forecast data download/management"""

from datetime import date
from typing import Any, Dict, List

import httpx

from meteoswiss_retriever.constants import BASE_URL, LOCAL_FORECAST_COLLECTION_ID
from meteoswiss_retriever.utils.date import get_date_from_str, get_datetime_from_iso_str

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
