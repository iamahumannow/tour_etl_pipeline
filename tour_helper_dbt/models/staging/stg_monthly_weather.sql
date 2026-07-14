with source as (
    select * from {{ source('raw', 'monthly_weather') }}
),

renamed as (
    select
        latitude::float as latitude,
        longitude::float as longitude,
        location,
        months,
        temperature_2m::float as temperature_2m,
        temperature_2m_max::float as temperature_2m_max,
        temperature_2m_min::float as temperature_2m_min,
        precipitation::float as precipitation,
        sunshine_duration::float as sunshine_duration,
        fetched_at::timestamp as fetched_at
    from source
        
)

select * from renamed

