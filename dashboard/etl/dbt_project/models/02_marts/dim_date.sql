with date_spine as (
    select * from {{ ref('date_spine') }}
),

date_dimension as (
    select
        date,
        extract(year from date) as year,
        extract(month from date) as month,
        extract(day from date) as day,
        extract(dow from date) as day_of_week,
        extract(doy from date) as day_of_year,
        extract(quarter from date) as quarter,
        case
            when extract(dow from date) in (0, 6) then true
            else false
        end as is_weekend,
        case
            when extract(month from date) in (12, 1, 2) then 'Winter'
            when extract(month from date) in (3, 4, 5) then 'Spring'
            when extract(month from date) in (6, 7, 8) then 'Summer'
            when extract(month from date) in (9, 10, 11) then 'Fall'
        end as season
    from date_spine
)

select * from date_dimension