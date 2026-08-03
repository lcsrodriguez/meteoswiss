# MeteoSwiss data retriever - `meteoswiss_retriever`

Python data retriever from MeteoSwiss open-data APIs.


## Data

> [!NOTE]
> This repository does not store any data provided by below providers. These scripts are downloading required datasets on the user's **local machine** only.

Datasets are downloaded from open-source APIs provided by MeteoSwiss.

1. **Local forecast data**: forecasts for 9 full days (including today)
    - https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data
2. **Short-term forecast data**: forecasts for the next minutes up to 6 hours ahead
    - https://opendatadocs.meteoswiss.ch/e-forecast-data/e1-short-term-forecast-data
3. **Ground-based measurements**:
    - Weather stations: https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations
    - Precipitation stations: https://opendatadocs.meteoswiss.ch/a-data-groundbased/a2-automatic-precipitation-stations
