-- Create schemas if they don't exist
create schema if not exists posthog;
create schema if not exists appsflyer;
create schema if not exists staging;
create schema if not exists analytics;

-- Generate test events data
create table if not exists posthog.events as
with test_data as (
    select
        generate_series(1, 1000) as id,
        case (random() * 5)::int
            when 0 then 'signup_started'
            when 1 then 'signup_completed'
            when 2 then 'profile_created'
            when 3 then 'first_property_added'
            when 4 then 'invite_sent'
            when 5 then 'invite_accepted'
        end as event,
        now() - (random() * interval '30 days') as timestamp,
        'user_' || (random() * 100)::int as distinct_id,
        '{}'::jsonb as properties,
        now() as created_at,
        now() as updated_at
)
select * from test_data;

-- Generate test installs data
create table if not exists appsflyer.installs as
with test_data as (
    select
        generate_series(1, 500) as id,
        now() - (random() * interval '30 days') as install_time,
        'user_' || (random() * 100)::int as customer_user_id,
        'com.home360.app' as app_id,
        case (random() * 1)::int
            when 0 then 'iOS'
            else 'Android'
        end as platform,
        'US' as country_code,
        case (random() * 1)::int
            when 0 then 'iPhone'
            else 'Android Phone'
        end as device_type,
        now() as created_at,
        now() as updated_at
)
select * from test_data;