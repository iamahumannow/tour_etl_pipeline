with base as (

    select
        fetch_date,
        location,
        flight_price
    from {{ ref('stg_hist_flight') }}

),

base_stats as (

    select
        fetch_date,
        location,
        flight_price,

        round(avg(flight_price) over (
            partition by location
            order by fetch_date
            rows between 3 preceding and current row
        ), 2) as rolling_4wk_avg,

        round(
            flight_price - lag(flight_price, 1) over (
                partition by location
                order by fetch_date
            ),
        2) as wow_change,

        round(
            div0(
                flight_price - lag(flight_price, 1) over (
                    partition by location
                    order by fetch_date
                ),
                lag(flight_price, 1) over (
                    partition by location
                    order by fetch_date
                )
            ) * 100,
        2) as wow_pct_change,

        round(
            flight_price - avg(flight_price) over (
                partition by location
            ),
        2) as vs_avg,

        case
            when flight_price < avg(flight_price) over (
                partition by location
            ) * 0.95 then 'Book Now'
            when flight_price > avg(flight_price) over (
                partition by location
            ) * 1.05 then 'Wait'
            else 'Neutral'
        end as price_signal,

        rank() over (
            partition by location
            order by flight_price asc
        ) as price_rank

    from base

)

select * from base_stats
order by location, fetch_date