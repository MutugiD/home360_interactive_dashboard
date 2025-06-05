{% macro generate_date_spine(start_date='2020-01-01', end_date='2025-12-31') %}

with date_spine as (
    select date_trunc('day', d)::date as date
    from generate_series(
        '{{ start_date }}'::date,
        '{{ end_date }}'::date,
        '1 day'::interval
    ) as d
)

select * from date_spine

{% endmacro %}