"""Sample script to retrieve + save metadata on forecasts"""

from meteoswiss_retriever.core.forecasts.metadata.parameters import (
    clean_parameters,
    query_parameters,
)
from meteoswiss_retriever.core.forecasts.metadata.points import (
    clean_points,
    query_geo_points,
)
from meteoswiss_retriever.utils.export import save_df

a = clean_points(query_geo_points())
b = clean_parameters(query_parameters())

save_df(a, "data/forecasts/metadata_points.csv")
save_df(b, "data/forecasts/metadata_parameters.csv")
