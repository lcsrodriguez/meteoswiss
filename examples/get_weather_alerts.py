"""Sample script to get weather alerts"""
# ruff: noqa: E402

from meteoswiss.utils.logs import setup_logger

setup_logger()

from meteoswiss.core.alerts.collector import (
    get_alerts_by_postal_code,
    parse_alerts_feed,
    query_alerts_feed,
)
from meteoswiss.utils.logs import get_logger

logger = get_logger(__name__)

alerts = parse_alerts_feed(query_alerts_feed())

relevant_alerts = get_alerts_by_postal_code(alerts, postal_code=6600)


print()
