with events as (
    select * from {{ ref('stg_events_raw') }}
),

invite_metrics as (
    select
        date_trunc('day', event_timestamp) as date,
        count(distinct case when event_name = 'invite_sent' then user_id end) as invites_sent,
        count(distinct case when event_name = 'invite_accepted' then user_id end) as invites_accepted
    from events
    where event_name in ('invite_sent', 'invite_accepted')
    group by 1
)

select * from invite_metrics