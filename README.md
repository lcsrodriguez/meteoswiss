# MeteoSwiss data retriever

Python weather data retriever from MeteoSwiss open-data: forecasts, ground measurements and weather alerts.

## Getting started

See sample scripts in **[`examples/`](examples/)** folder.

## Data

> [!NOTE]
> This repository does not store any data provided by below providers. These scripts are downloading required datasets on the user's **local machine** only.

Datasets are available via open-source APIs provided by MeteoSwiss.

1. **Local forecast data**: forecasts for 9 full days (including today)
    - https://opendatadocs.meteoswiss.ch/e-forecast-data/e4-local-forecast-data
2. **Short-term forecast data**: forecasts for the next minutes up to 6 hours ahead
    - https://opendatadocs.meteoswiss.ch/e-forecast-data/e1-short-term-forecast-data
3. **Ground-based measurements**:
    - Weather stations: https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations
    - Precipitation stations: https://opendatadocs.meteoswiss.ch/a-data-groundbased/a2-automatic-precipitation-stations

> [!WARNING]
> Short-term forecast data *(nowcasting)* are available to download **on request**. No API endpoint exposed.


### Measurements

When selecting a postal code, users can have access to local forecasts at this postal code.
However, ground-measurements are only available on specific stations.
To get both *realized* measurements + local forecasts for a given postal code,
we can use **proxy measurements** by picking the ground measurements at the nearest station from our postal code coordinates.


### Weather alerts

We wanted to include weather alerts retrieval in this package. However, it does not seem to be available as an open data source directly by MeteoSwiss.

However, MeteoSwiss distributes its weather alerts directly to **[MeteoAlarm.org](https://meteoalarm.org/en)** which provides APIs or ATOM feed like this one: https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-switzerland

> [!WARNING]
> Legacy RSS feeds (`https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-rss-<COUNTRY_NAME>`) are deprecated and must not be used! Only use ATOM feeds.

Docs on ATOM format: https://en.wikipedia.org/wiki/Atom_(web_standard)

## License

Data source: **[MeteoSwiss](https://opendatadocs.meteoswiss.ch/)**.
