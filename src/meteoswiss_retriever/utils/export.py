"""Logic to export datasets"""

import polars as pl

from meteoswiss_retriever.constants import CSV_SEPARATOR


def save_df(df: pl.DataFrame, path: str) -> bool:
    """
    Save a Polars dataframe to csv on disk
    :param df: Polars dataframe
    :type df: pd.DataFrame
    :param path: Path to save dataframe
    :type path: str
    :return: Boolean to indicate if dataframe was successfully saved on disk
    :rtype: bool
    """
    try:
        df.write_csv(path, separator=CSV_SEPARATOR)
        return True
    except Exception as exc_:
        print(exc_)
        return False
