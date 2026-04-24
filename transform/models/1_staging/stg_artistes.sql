with source as (
    select * from {{ source('lake', 'artists_search') }}
),

data as (
    select
        spotify_id as artiste_id,
        trim(name) as nom,
        source_genre as style

    from source

    where
        spotify_id is not null
        and trim(name) != ''
)

select * from data