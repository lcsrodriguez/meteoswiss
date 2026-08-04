"""Sub-module to query and return MeteoSwiss parameters"""

from io import StringIO

import httpx
import polars as pl

from meteoswiss_retriever.constants import (
    BASE_URL,
    LOCAL_FORECAST_COLLECTION_ID,
    REMOVED_LANGUAGES,
)


def query_parameters(raise_errors: bool = True) -> pl.DataFrame:
    """
    Function to retrieve and return MeteoSwiss parameters
    (see docs: https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data?metadata=parameters)
    :param raise_errors: Raising errors if HTTP exception occurs
    :type raise_errors: bool
    :return: Polars DataFrame with parameters from MeteoSwiss
    :rtype: pl.DataFrame
    """

    r = httpx.get(
        url=f"{BASE_URL}/{LOCAL_FORECAST_COLLECTION_ID}/ogd-local-forecasting_meta_parameters.csv",
    )
    if raise_errors:
        r.raise_for_status()

    return pl.read_csv(StringIO(r.text), separator=";")


def clean_parameters(parameters: pl.DataFrame) -> pl.DataFrame:
    """
    Function to clean queried parameters
    :param parameters: Queried parameters
    :type parameters: pl.DataFrame
    :return: Cleaned parameters
    :rtype: pl.DataFrame
    """
    return parameters.drop(
        [f"parameter_description_{lang}" for lang in REMOVED_LANGUAGES]
        + [f"parameter_group_{lang}" for lang in REMOVED_LANGUAGES]
    )
