with source as(
    select * from {{ source('raw','weather') }}
),

renamed as (
    select
        latitude::NUMBER(9,4) as latitude,
        longitude::NUMBER(9,4) as longitude,
        elevation::NUMBER(7,1) as elevation,
        hour_date::date as hour_date,
        TIME_FROM_PARTS(
            FLOOR(hour_time / 3600000000000),
            FLOOR(MOD(hour_time, 3600000000000) / 60000000000),
            FLOOR(MOD(hour_time, 60000000000) / 1000000000)
        ) AS hour_time,
        hour_temp::NUMBER(5,1) as hour_temp,
        hour_precipitation::NUMBER(3,1) as hour_precipitation,
        fetched_at::timestamp as fetched_at,
        location
    from source
)

select * from renamed