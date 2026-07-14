with source as (
    select * from {{ source('raw', 'monthly_hotel') }}
),

renamed as (
    select
        months,
        price::NUMBER(10,2) as price,
        location,
        fetched_at::timestamp as fetched_at
    from source
        
),

base as (
    select
        *,
        last_value(price ignore nulls) over(
            partition by location
            order by months
            rows between unbounded preceding and 1 preceding
        ) as prev_value,
        first_value(price ignore nulls) over(
            partition by location
            order by months
            rows between 1 following and unbounded following
        ) as next_value,
        price is NULL as is_stg_imputed
    from renamed
),

mart_imputed as (
    select
        *,
        {{ impute_null('price','prev_value','next_value', 'location') }} as imputed_price,
    from base
)

select * from mart_imputed

