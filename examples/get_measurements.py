"""Sample script to retrieve + save metadata on ground measurements"""
# ruff: noqa: E402

from meteoswiss.utils.logs import get_logger, setup_logger

setup_logger()

from meteoswiss.core.measurements.ground_measurements import (
    collect_assets_data,
    query_available_items,
    query_measurements_asset_links,
)
from meteoswiss.core.measurements.metadata.parameters import (
    clean_parameters,
    query_parameters,
)
from meteoswiss.core.measurements.metadata.stations import (
    clean_stations,
    query_stations,
)
from meteoswiss.utils.export import save_df

logger = get_logger(__name__)

stations = clean_stations(query_stations())
parameters = clean_parameters(query_parameters())

save_df(stations, "data/measurements/metadata_stations.csv")
save_df(parameters, "data/measurements/metadata_parameters.csv")

features = query_available_items()
assets_links = query_measurements_asset_links(station_abbr="PUY")

collect_assets_data(assets_links)

print()
