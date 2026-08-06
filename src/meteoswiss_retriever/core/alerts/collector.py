"""Logic to collect and parse an ATOM feed from MeteoAlarm"""

from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np
import polars as pl
from feedparser import parse
from feedparser.util import FeedParserDict
from shapely.geometry import Point, Polygon

from meteoswiss_retriever.constants import CURRENT_TZ, WEATHER_ALERT_ATOM_FEED_PREFIX
from meteoswiss_retriever.core.forecasts.metadata.points import (
    clean_points,
    get_point_by_postal_code,
    query_geo_points,
)
from meteoswiss_retriever.utils.geo import parse_polygon
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)


def query_alerts_feed(country: str = "switzerland") -> FeedParserDict:
    """
    Function to retrieve and returned a dict representing a parsed feed
    (see package `feedparser`)
    :param country: Country string
    :type country: str
    :return: Dictionary of alert entries from `feedparser` package
    :rtype: FeedParserDict
    """
    feed: FeedParserDict = parse(f"{WEATHER_ALERT_ATOM_FEED_PREFIX}{country.lower()}")
    return feed


def parse_alerts_feed(
    feed: FeedParserDict | None = None,
) -> List[Dict[str, str | datetime | List[Tuple[np.float64, ...]]]]:
    """
    Function to parse a `feedparser` **FeedParserDict** object and return a list of clean alerts
    :param feed: FeedParserDict object
    :type feed: FeedParserDict
    :return: List of clean alerts
    :rtype: List[Dict[str, str | datetime | List[Tuple[np.float64, ...]]]]
    """
    if feed is None:
        logger.error("No feed found")
        return []

    if not feed.entries:
        logger.error("No feed entries found")
        return []

    entries: List[Dict[str, str | datetime | List[Tuple[np.float64, ...]]]] = []

    for entry in feed.entries:
        entries.append(
            {
                "geo_polygon": parse_polygon(
                    str_polygon=entry["cap_polygon"]
                ),  # entry["cap_polygon"],
                "geo_name": entry["cap_areadesc"],
                "event": entry["cap_event"],
                "certainty": entry["cap_certainty"],
                "severity": entry["cap_severity"],
                "urgency": entry["cap_urgency"],
                "scope": entry["cap_scope"],
                "message_type": entry["cap_message_type"],
                "status": entry["cap_status"],
                "dt_published": datetime.fromisoformat(entry["published"]).astimezone(
                    tz=CURRENT_TZ
                ),
                "dt_updated": datetime.fromisoformat(entry["updated"]).astimezone(
                    tz=CURRENT_TZ
                ),
                "dt_sent": datetime.fromisoformat(entry["cap_sent"]).astimezone(
                    tz=CURRENT_TZ
                ),
                "dt_expires": datetime.fromisoformat(entry["cap_expires"]).astimezone(
                    tz=CURRENT_TZ
                ),
                "dt_effective": datetime.fromisoformat(
                    entry["cap_effective"]
                ).astimezone(tz=CURRENT_TZ),
                "dt_onset": datetime.fromisoformat(entry["cap_onset"]).astimezone(
                    tz=CURRENT_TZ
                ),
            }
        )
    return entries


def get_alerts_by_postal_code(
    alerts: List[Dict[str, str | datetime | List[Tuple[np.float64, ...]]]],
    postal_code: int | None = None,
) -> List[Dict]:
    """
    Function to get alerts for a given postal code
    :param alerts: Dict of alert entries
    :type alerts: List[Dict[str, str | datetime | List[Tuple[np.float64, ...]]]]
    :param postal_code: Postal code
    :type postal_code: int | None
    :return: List of relevant alerts for this area
    :rtype: List[Dict]
    """
    if postal_code is None:
        logger.error("No postal code found")
        return []

    # Getting points representing a postal code
    points = clean_points(query_geo_points()).filter(pl.col("point_type_id") == 2)

    postal_code_details = get_point_by_postal_code(data=points, postal_code=postal_code)

    # Getting geo details from given postal code
    point_geo = postal_code_details.select("lon", "lat").to_dict(as_series=False)
    point_lon, point_lat = (point_geo["lon"][0], point_geo["lat"][0])

    p = Point(point_lon, point_lat)

    relevant_alerts: List[Dict] = []
    for i, alert in enumerate(alerts):
        if alert["dt_expires"] < datetime.now().astimezone(tz=CURRENT_TZ):  # type: ignore[operator]
            logger.warning(f"Alert #{i} expired. Skipping....")
            continue

        alert_poly: Polygon = Polygon(alert["geo_polygon"])

        if alert_poly.covers(p):
            logger.error(f"Alert #{i} contains this postal code")
            relevant_alerts.append(alert)

    return relevant_alerts
