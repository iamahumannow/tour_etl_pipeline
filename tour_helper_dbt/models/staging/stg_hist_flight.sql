with source as (
    select * from {{ source('raw', 'hist_flight') }}
),

renamed as (
    select
        fetched_at::date        as fetch_date,
        location,
        price::float as flight_price
    from source
)

select * from renamed