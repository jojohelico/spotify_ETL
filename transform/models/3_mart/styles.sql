with styles as (
    select
        distinct(style)
    
    from {{ ref('stg_artistes') }}
)

select * from styles