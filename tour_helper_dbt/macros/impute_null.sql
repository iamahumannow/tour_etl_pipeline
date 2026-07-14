{% macro impute_null(column, prev_value, next_value, partition_by) %}

    case
        when {{column}} is NOT null
            then {{column}}
        
        when {{prev_value}} is NOT null and
        {{next_value}} is NOT null
            then  round(({{prev_value}}+{{next_value}})/2,2)
        
        when {{prev_value}} is not null
            then {{prev_value}}

        when {{next_value}} is not null
            then {{next_value}}
        
        else round(
            avg({{column}}) over(
                partition by {{partition_by}}
            )
            ,2
        )
    END

{% endmacro %}