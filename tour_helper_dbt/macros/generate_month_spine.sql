{% macro generate_month_spine() %}

    with months as (
        select 'January'  as months union all
        select 'February'  union all
        select 'March'  union all
        select 'April'  union all
        select 'May'  union all
        select 'June'  union all
        select 'July'  union all
        select 'August'  union all
        select 'September'  union all
        select 'October' union all
        select 'November' union all
        select 'December'
    ),

    location as (
        select distinct location
        from {{ ref('stg_monthly_weather') }}
    )

    select
        l.location,
        m.months
    from location l
    cross join months m

{% endmacro %}