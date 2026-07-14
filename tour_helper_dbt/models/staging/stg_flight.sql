with source as (
    select * from {{ source('raw', 'flight') }}
),

renamed as (
    select
        airline,
        airplane,
        departure_date::date as departure_date,
        departure_time::time as departure_time,
        arrival_date::date as arrival_date,
        arrival_time::time as arrival_time,
        duration,
        leg_room,
        price::NUMBER(11,2) as price,
        flight_number,
        fetched_at::timestamp as fetched_at,
        location
    from source
        
)

select * from renamed

