with source as (
    select * from {{ source('posthog', 'events') }}
),

renamed as (
    select
        id as event_id,
        event as event_name,
        timestamp as event_timestamp,
        distinct_id as user_id,
        properties,
        created_at,
        updated_at
    from source
)

select * from renamed