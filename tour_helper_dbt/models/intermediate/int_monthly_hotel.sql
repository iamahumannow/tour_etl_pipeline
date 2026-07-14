with months_spine as (
    select * from {{ref('int_month_spine')}}
),

hotel_data as (
    select
        *
    from {{ ref('stg_monthly_hotel') }}
),

hotel_agg as (
    select
        s.location,
        s.months,
        h.imputed_price,
        h.prev_value,
        h.next_value,
        h.imputed_price is NULL as is_int_imputed,
        h.is_stg_imputed
    from months_spine s
    left join hotel_data h
    on s.location = h.location
    and s.months = h.months
),

mart_imputed as (
    select
        *,
        {{ impute_null('imputed_price','prev_value','next_value', 'location') }} as avg_hotel_price,
    from hotel_agg
)

select * from mart_imputed
