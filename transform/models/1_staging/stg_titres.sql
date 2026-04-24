
with source as (
    select * from {{ source('lake', 'titres') }}
),

data as (
    select
        spotify_id as titre_id,
        trim(name) as libelle,
        duration_ms / 1000 as duree,
        extracted_at as date_creation,
        spotify_url as url_ecoute,
        track_number,
        album_id,
        is_playable,
        explicit

    from source

    where
        spotify_id is not null
)

select * from data