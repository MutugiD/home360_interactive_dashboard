with source as (
    select * from {{ source('appsflyer', 'installs') }}
),

renamed as (
    select
        id as install_id,
        install_time as install_timestamp,
        customer_user_id as user_id,
        app_id,
        platform,
        country_code,
        device_type,
        created_at,
        updated_at
    from source
)

select * from renamed