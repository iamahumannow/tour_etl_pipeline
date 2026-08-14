# TripLens

An end-to-end data pipeline that extracts weather, flight, and hotel data across multiple destinations, orchestrated with Airflow, transformed with dbt on Snowflake, and visualised in Power BI to provide the best time and place to travel.

## Architecture
Workflow:
Architecture:
<img width="962" height="362" alt="Untitled Diagram drawio" src="https://github.com/user-attachments/assets/540aef5b-3919-489d-a05a-127ccdc3d869" />

dbt models:
<img width="2239" height="1127" alt="Screenshot 2026-08-07 153356" src="https://github.com/user-attachments/assets/4d68af74-1d9c-4ea5-b027-f9cad086690a" />

dbt Lineage:
<img width="2112" height="718" alt="Screenshot 2026-08-07 153251" src="https://github.com/user-attachments/assets/7b31abb0-cae1-46b2-b386-59badb6881d1" />


## Tech Stack
- Extraction: Python, requests, pandas
- Orchestration: Apache Airflow (Docker)
- Storage: Snowflake, MYSQL
- Transformation: dbt (staging + marts)
- Visualization: Power BI
- Data Quality: dbt tests, tiered null imputation

## Pipeline Overview
- trip_helper_setup DAG: one-time load of weather, hotels, flights, monthly snapshots, best_time computation
- flight_price_tracker DAG: weekly recurring flight price tracking

## dbt Models
 - Staging: stg_weather, stg_historical_weather, stg_flights, stg_hotels, 
          stg_monthly_flight, stg_monthly_hotel, 
          stg_hist_flight
- Intermediate: int_month_spine, int_monthly_flight, int_monthly_hotel
- Marts: mart_best_time, mart_hist_flight
- Macros: normalize(), impute_null()

## Key Engineering Decisions
- Two DAGs for different cadences
	-- One DAG contains a schedule interval, mixing them is not ideal. Seperate DAGs also isolates failures.
  
- Month spine guarantees 36 rows regardless of API gaps
	-- Encountered issues where api failed to issue some months' data, which would have caused issues creating heatmap. This spine guarantees completeness regardless of upstream API gaps.

- Monthly price proxy via representative week, not exhaustive calls
	-- Fetching every date for a year would require hundreds of API calls per destination per run, exceeding rate limits. A representative week reveals the seasonal pricing pattern which is the signal we are looking for.

- Composite score: 55% weather, 45% price weighting
	-- Assigned weights based on personal preference. The weights are configurable in the mart model if a different profile is needed. 

- Tiered null imputation: interpolation -> forward fill -> backward fill -> destination average
	-- A tiered approach that handles every case :consecutive nulls, leading nulls, trailing nulls.

- Direct Snowflake loading via key pair authentication
	-- Snowflake's recommended method for programmatic access and standard approach in production DE environments.

- Per-destination failure isolation in the task graph
	-- One destination failure does not stop the entire DAG, the specific task is marked and rest of calls are made and stored. This makes debugging easier and data collection more resilient. 

- dbt tests as quality gates in the Airflow pipeline
	-- Added singular tests along with generic tests to assure data quality before reaching Power BI.


## Live Dashboard
Dashboard Link:
https://app.powerbi.com/links/ByG5g5ujzv?ctid=187ca15f-54e0-4673-86f6-b6d7f4c75eef&pbi_source=linkShare


## Known Limitations
- Some Flight prices were imputed due to API data gaps
- Snowflake free tier used — warehouse suspended
- Historical flight tracking requires ongoing pipeline runs to accumulate trend data
- Full refresh-style processing is used for some models which leads to inefficiency
- Currently not desinged for real-time data processing

## Future Improvements
- Add pandera schema validation at the extraction layer so bad data is caught before -- currently dbt catches it post loading.
- Add an Airflow SLA miss configuration on the flight_price_tracker DAG to flag if the weekly run hasn't completed within an expected window.
- Migrate from local to cloud-hosted Airflow so pipeline runs independent of the state of local machine.
- Add a user budget input that filters destinations and months to only those within a specified total trip cost.
- Add incremental materialisation to mart_hist_flight so it only processes new hist_flight rows on each dbt run rather than rebuilding the full table weekly.
- Add an option in Power BI allowing users to adjust the 55/45 weather-to-price weighting and see how the best_time rankings change without reloading pipeline.
