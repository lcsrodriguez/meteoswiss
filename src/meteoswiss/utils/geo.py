"""Math logic to handle geo coordinates"""

# import math
from typing import List, Tuple

import numpy as np
import polars as pl


def computer_haversine_dist(
    lon_point: float, lat_point: float, lon_col, lat_col
) -> pl.Series:
    """
    Function to compute the Haversine distance between a point of interest and 2 lon/lat columns
    :param lon_point: Point longitude
    :type lon_point: float
    :param lat_point: Point latitude
    :type lat_point: float
    :param lon_col: Longitude column
    :type lon_col:
    :param lat_col: Latitude column
    :type lat_col:
    :return: Distance to km column/pl.Series (newly-created)
    :rtype: pl.Series
    """
    R: float = 6371.0  # Earth radius

    lat_point_rad = np.radians(lat_point)
    lon_point_rad = np.radians(lon_point)

    lat2_rad = lat_col.radians()
    lon2_rad = lon_col.radians()

    dlat = lat2_rad - lat_point_rad
    dlon = lon2_rad - lon_point_rad

    a = (dlat / 2).sin() ** 2 + np.cos(lat_point_rad) * lat2_rad.cos() * (
        dlon / 2
    ).sin() ** 2
    c = 2 * a.sqrt().arcsin()

    return R * c


def parse_polygon(str_polygon: str) -> List[Tuple[np.float64, ...]]:
    """
    Function to parse a string representing a polygon into a list of corresponding points
    :param str_polygon: String representing a polygon
    :type str_polygon: str
    :return: List of points (tuple := (lon, lat))
    :rtype: List[Tuple[np.float64, ...]]
    """
    return [
        tuple(reversed(tuple(map(lambda s: np.float64(s), point.split(",")))))
        for point in str_polygon.split(" ")
    ]


# Adding geo-fencing (check if a point is inside a polygon or not)
# check formula and optimized ways
