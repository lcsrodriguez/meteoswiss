"""Sample script to retrieve + save metadata on forecasts"""
# ruff: noqa: E402

from meteoswiss.utils.logs import get_logger, setup_logger

setup_logger()


from meteoswiss.core.forecasts.local_forecast import (
    get_forecast_data,
    query_local_forecast_asset_links,
    read_local_data,  # , collect_assets_data
)
from meteoswiss.core.forecasts.metadata.parameters import (
    clean_parameters,
    get_parameters_by_freq,
    query_parameters,
)
from meteoswiss.core.forecasts.metadata.points import (
    Location,
    clean_points,
    query_geo_points,
)
from meteoswiss.utils.export import save_df

logger = get_logger(__name__)

points = clean_points(query_geo_points())
params = clean_parameters(query_parameters())

save_df(points, "data/forecasts/metadata_points.csv")
save_df(params, "data/forecasts/metadata_parameters.csv")


# q = get_available_forecast_days(query_available_items())

links = query_local_forecast_asset_links()


h = get_parameters_by_freq(params)
# forecasts_data = collect_assets_data(links)

forecasts_data = read_local_data(params["parameter_shortname"].to_list())

forecasts_data_2 = get_forecast_data(
    forecasts_data, Location(101200, 2), parameters=params
)

save_df(forecasts_data_2["H"], "data/forecasts/forecasts_all_H.csv")
save_df(forecasts_data_2["D"], "data/forecasts/forecasts_all_D.csv")

print()
