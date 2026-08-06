"""Sample script to get weather alerts"""
# ruff: noqa: E402

from meteoswiss_retriever.utils.logs import setup_logger

setup_logger()

from meteoswiss_retriever.core.alerts.collector import (
    parse_alerts_feed,
    query_alerts_feed,
)
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)

alerts = parse_alerts_feed(query_alerts_feed())

print()
