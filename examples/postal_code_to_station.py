"""Sample script to get measurements nearest station from a given postal code"""
# ruff: noqa: E402

from meteoswiss_retriever.utils.logs import setup_logger

setup_logger()

import polars as pl

from meteoswiss_retriever.core.forecasts.metadata.points import (
    clean_points,
    get_point_by_postal_code,
    query_geo_points,
)
from meteoswiss_retriever.core.measurements.metadata.stations import (
    clean_stations,
    query_stations,
)
from meteoswiss_retriever.utils.geo import computer_haversine_dist
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)


POSTAL_CODE: int = 1012

# Retrieving points + stations
points = clean_points(query_geo_points())
stations = clean_stations(query_stations())

postal_code_details = get_point_by_postal_code(data=points, postal_code=POSTAL_CODE)

# Getting geo details from given postal code
point_geo = postal_code_details.select("lon", "lat").to_dict(as_series=False)
point_lon, point_lat = (point_geo["lon"][0], point_geo["lat"][0])

# Getting distance ranking (nearest to furthest) from postal code point
stations_ranked = (
    stations.with_columns(
        distance_km=computer_haversine_dist(
            point_lon, point_lat, pl.col("lon"), pl.col("lat")
        )
    ).sort("distance_km")
).select("station_abbr", "station_name", "station_canton", "lon", "lat", "distance_km")


nearest_station_from_postal_code = stations_ranked.head(1)

print()
