"""Logic to collect and parse an ATOM feed from MeteoAlarm"""

from typing import Dict, List

from feedparser import parse
from feedparser.util import FeedParserDict

from meteoswiss_retriever.constants import WEATHER_ALERT_ATOM_FEED_PREFIX
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


def parse_alerts_feed(feed: FeedParserDict | None = None) -> List[Dict]:
    """
    Function to parse a `feedparser` **FeedParserDict** object and return a list of clean alerts
    :param feed: FeedParserDict object
    :type feed: FeedParserDict
    :return: List of clean alerts
    :rtype: List[Dict]
    """
    if feed is None:
        logger.error("No feed found")
        return []

    if not feed.entries:
        logger.error("No feed entries found")
        return []

    entries: List[Dict] = []

    for entry in feed.entries:
        entries.append(
            {
                "geo_polygon": entry["cap_polygon"],
                "geo_name": entry["cap_areadesc"],
                "event": entry["cap_event"],
                "certainty": entry["cap_certainty"],
                "severity": entry["cap_severity"],
                "urgency": entry["cap_urgency"],
                "scope": entry["cap_scope"],
                "message_type": entry["cap_message_type"],
                "status": entry["cap_status"],
                "dt_published": entry["published"],
                "dt_updated": entry["updated"],
                "dt_sent": entry["cap_sent"],
                "dt_expires": entry["cap_expires"],
                "dt_effective": entry["cap_effective"],
                "dt_onset": entry["cap_onset"],
            }
        )
    return entries
