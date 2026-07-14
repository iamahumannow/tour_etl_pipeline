with months_spine as (
    select * from {{ref('int_month_spine')}}
),

flight_data as (
    select
        *
    from {{ ref('stg_monthly_flight') }}
),

flight_agg as (
    select
        s.location,
        s.months,
        f.imputed_price,
        f.prev_value,
        f.next_value,
        f.imputed_price is NULL as is_int_imputed,
        f.is_stg_imputed
    from months_spine s
    left join flight_data f
    on s.location = f.location
    and s.months = f.months    
),

mart_imputed as (
    select
        *,
        {{ impute_null('imputed_price','prev_value','next_value', 'location') }} as avg_flight_price,
    from flight_agg
)

select * from mart_imputed
