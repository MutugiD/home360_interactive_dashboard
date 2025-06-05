with events as (
    select * from {{ ref('stg_events_raw') }}
),

funnel_steps as (
    select
        date_trunc('day', event_timestamp) as date,
        case
            when event_name = 'signup_started' then 'Started'
            when event_name = 'signup_completed' then 'Completed'
            when event_name = 'profile_created' then 'Profile Created'
            when event_name = 'first_property_added' then 'First Property'
        end as step_name,
        count(distinct user_id) as user_count
    from events
    where event_name in (
        'signup_started',
        'signup_completed',
        'profile_created',
        'first_property_added'
    )
    group by 1, 2
)

select * from funnel_steps