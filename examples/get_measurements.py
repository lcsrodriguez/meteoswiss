"""Sample script to retrieve + save metadata on ground measurements"""
# ruff: noqa: E402

from meteoswiss_retriever.utils.logs import get_logger, setup_logger

setup_logger()

from meteoswiss_retriever.core.measurements.metadata.parameters import (
    clean_parameters,
    query_parameters,
)
from meteoswiss_retriever.core.measurements.metadata.stations import (
    clean_stations,
    query_stations,
)
from meteoswiss_retriever.utils.export import save_df

logger = get_logger(__name__)

stations = clean_stations(query_stations())
parameters = clean_parameters(query_parameters())

save_df(stations, "data/measurements/metadata_stations.csv")
save_df(parameters, "data/measurements/metadata_parameters.csv")

print()
