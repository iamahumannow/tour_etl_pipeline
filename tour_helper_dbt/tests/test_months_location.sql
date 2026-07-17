select *
from (
    select count(*) as total_rows
    from {{ ref('mart_best_time') }}
) counts
where total_rows != 36