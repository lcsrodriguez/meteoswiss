"""Sub-module to query and return MeteoSwiss parameters"""

from io import StringIO
from typing import Dict, List

import httpx
import polars as pl

from meteoswiss_retriever.constants import (
    BASE_URL,
    ENCODING_FORMAT,
    LOCAL_FORECAST_COLLECTION_ID,
    REMOVED_LANGUAGES,
)
from meteoswiss_retriever.utils.logs import get_logger

logger = get_logger(__name__)


def query_parameters(raise_errors: bool = True) -> pl.DataFrame:
    """
    Function to retrieve and return MeteoSwiss parameters
    (see docs: https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data?metadata=parameters)
    :param raise_errors: Raising errors if HTTP exception occurs
    :type raise_errors: bool
    :return: Polars DataFrame with parameters from MeteoSwiss
    :rtype: pl.DataFrame
    """

    logger.info("Querying MeteoSwiss local forecast parameters (metadata)")
    r = httpx.get(
        url=f"{BASE_URL}/{LOCAL_FORECAST_COLLECTION_ID}/ogd-local-forecasting_meta_parameters.csv",
    )
    if raise_errors:
        r.raise_for_status()

    return pl.read_csv(StringIO(r.content.decode(ENCODING_FORMAT)), separator=";")


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


def get_parameters_freq(parameters: pl.DataFrame) -> Dict[str, str]:
    """
    Function returning frequency for each parameter
    :param parameters: Dataframe of parameters
    :type parameters: pl.DataFrame
    :return: Dictionary with frequency for each parameter
    :rtype: Dict[str, str]
    """
    logger.info("Getting parameter frequencies")
    freqs: Dict[str, List[str]] = parameters.select(
        pl.col("parameter_shortname"), pl.col("parameter_granularity")
    ).to_dict(as_series=False)
    return {
        k: v
        for k, v in list(
            zip(freqs["parameter_shortname"], freqs["parameter_granularity"])
        )
    }


def get_parameters_by_freq(parameters: pl.DataFrame) -> Dict[str, List[str]]:
    """
    Function to return list of parameter names grouped by frequency (H or D)
    :param parameters: Dataframe of parameters
    :type parameters:  pl.DataFrame
    :return: Dictionary with frequency for each parameter
    :rtype: Dict[str, List[str]]
    """
    freqs = get_parameters_freq(parameters)

    r: Dict[str, List[str]] = {}
    for v, k in freqs.items():
        if k not in r:
            r[k] = []
        r[k].append(v)
    return r
