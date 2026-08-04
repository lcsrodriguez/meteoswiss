"""List of constants"""

from typing import List

from pytz import timezone  # type: ignore[import-untyped]

BASE_URL: str = "https://data.geo.admin.ch"

LOCAL_FORECAST_COLLECTION_ID: str = "ch.meteoschweiz.ogd-local-forecasting"

REMOVED_LANGUAGES: List[str] = ["de", "fr", "it"]

# docs: https://pypi.org/project/pytz/
CURRENT_TZ = timezone("Europe/Zurich")
