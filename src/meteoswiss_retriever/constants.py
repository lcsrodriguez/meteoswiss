"""List of constants"""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Dict, List, Tuple

from platformdirs import user_log_path
from pytz import timezone  # type: ignore[import-untyped]

APP_NAME: str = "meteoswiss_retriever"

# Version dynamically updated via Makefile targets
APP_VERSION: str = version(APP_NAME)
APP_VERSION_TUPLE: Tuple[int, ...] = tuple(map(int, APP_VERSION.split(".")))

try:
    __version__: str = version(APP_NAME)
except PackageNotFoundError:
    __version__ = "unknown"  # "0.0.0"


BASE_URL: str = "https://data.geo.admin.ch"

LOCAL_FORECAST_COLLECTION_ID: str = "ch.meteoschweiz.ogd-local-forecasting"
GROUND_MEASUREMENTS_COLLECTION_ID: str = "ch.meteoschweiz.ogd-smn"

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


CSV_SEPARATOR: str = ";"

LOG_DIR: Path = user_log_path(appname=APP_NAME, version=APP_VERSION)

# https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-switzerland
WEATHER_ALERT_ATOM_FEED_PREFIX: str = (
    "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-"
)
