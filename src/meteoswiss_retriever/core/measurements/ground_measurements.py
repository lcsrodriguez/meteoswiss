"""Logic to handle local forecast data download/management"""

from typing import Any

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

    print()

    latest_update = get_datetime_from_iso_str(data["timeStamp"])
    logger.info(f"Latest update of the collection: {latest_update}")
    return data["features"]
