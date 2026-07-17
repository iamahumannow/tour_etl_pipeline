select location
from {{ ref('mart_best_time') }}
group by location
having count(distinct best_time_rank) != 12