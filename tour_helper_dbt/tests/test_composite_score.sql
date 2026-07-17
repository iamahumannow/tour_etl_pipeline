select *
from {{ ref('mart_best_time') }}
where overall_score < 0
   or overall_score > 1