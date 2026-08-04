"""List of constants"""

from typing import Dict, List

from pytz import timezone  # type: ignore[import-untyped]

BASE_URL: str = "https://data.geo.admin.ch"

LOCAL_FORECAST_COLLECTION_ID: str = "ch.meteoschweiz.ogd-local-forecasting"

REMOVED_LANGUAGES: List[str] = ["de", "fr", "it"]

# docs: https://pypi.org/project/pytz/
CURRENT_TZ = timezone("Europe/Zurich")

# docs: https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data?metadata=points
FORECAST_POINTS_MAPPING: Dict[int, str] = {
    1: "WEATHER_STATION",
    2: "POSTAL_CODE",
    3: "POINT_OF_INTEREST",
}


# docs: https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data?metadata=points#data-format
# CSV encoding := **Latin1** (ISO-8859-1)

ENCODING_FORMAT: str = "latin-1"
