with source as(
    select * from {{ source('raw','hotel') }}
),

renamed as (
    select
        name,
        stay_type,
        rating,
        noPeople as no_people,
        beds,
        bedroom,
        bathroom,
        check_in_out,
        close_to_airport,
        fetched_at::timestamp as fetched_at,
        price::NUMBER(10,2) as price,
        location
    from source
)

select * from renamed
