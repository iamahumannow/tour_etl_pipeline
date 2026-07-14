{% macro normalize(column, partition_by) %}

    DIV0(
        {{ column }} - min({{ column }}) over (partition by {{ partition_by }}),
        max({{ column }}) over (partition by {{ partition_by }})
         - min({{ column }}) over (partition by {{ partition_by }})
    )

{% endmacro %}