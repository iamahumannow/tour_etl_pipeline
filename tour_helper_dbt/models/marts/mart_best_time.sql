with weather_agg as(
    select
        location,
        months,
        temperature_2m as avg_temp,
        temperature_2m_min as avg_temp_min,
        precipitation as avg_rain,
        sunshine_duration as avg_sunshine
    from {{ ref('stg_monthly_weather') }}
),

flight_agg as (
    select
        *
    from {{ ref('int_monthly_flight') }}
),

hotel_agg as (
    select
        *
    from {{ ref('int_monthly_hotel') }}
),

joined_agg as (
    select
        f.location,
        f.months,
        w.avg_temp,
        w.avg_temp_min,
        w.avg_rain,
        w.avg_sunshine,
        f.avg_flight_price,
        h.avg_hotel_price
    from flight_agg as f
    left join weather_agg w
        on w.location = f.location and
        w.months = f.months
    left join hotel_agg h
        on w.location = h.location and
        w.months = h.months
),


normalised_data as (
    select
        location,
        months,
        avg_temp,
        avg_temp_min,
        avg_rain,
        avg_sunshine,
        avg_flight_price,
        avg_hotel_price,
        
        {{ normalize('avg_sunshine', 'location') }}  as sunshine_score,

        1 - {{ normalize('avg_temp', 'location') }}          as temp_score,
        1 - {{ normalize('avg_temp_min', 'location') }}      as temp_min_score,
        1 - {{ normalize('avg_rain', 'location') }}          as rain_score,
        1 - {{ normalize('avg_flight_price', 'location') }}  as flight_price_score,
        1 - {{ normalize('avg_hotel_price', 'location') }}   as hotel_price_score
    
    from joined_agg
),

score_data as (
    select
        location,
        months,
        avg_temp,
        avg_temp_min,
        avg_rain,
        avg_sunshine,
        avg_flight_price,
        avg_hotel_price,
        sunshine_score,
        temp_score,
        temp_min_score,
        rain_score,
        round(((temp_score*0.3)+
            (temp_min_score*0.25)+
            (rain_score*0.25)+
            (sunshine_score*0.2))
            ,2) as weather_score,
        flight_price_score,
        hotel_price_score,
        round(
            weather_score*0.55 
            + (flight_price_score*0.23)
            + (hotel_price_score*0.22)
        ,2) as overall_score
    from normalised_data
),

final_data as (
    select
        location,
        months,
        avg_temp,
        avg_temp_min,
        avg_rain,
        avg_sunshine,
        avg_flight_price,
        avg_hotel_price,
        round(sunshine_score,2) as sunshine_score,
        round(temp_score,2) as temp_score,
        round(temp_min_score,2) as temp_min_score,
        round(rain_score,2) as rain_score,
        weather_score,
        round(flight_price_score,2) as flight_price_score,
        round(hotel_price_score,2) as hotel_price_score,
        overall_score,

        row_number() over (
            order by overall_score desc
        ) as best_time_rank

    from score_data
)

select * from final_data
order by location, months