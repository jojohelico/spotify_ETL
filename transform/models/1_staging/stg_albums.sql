-- models/staging/stg_albums.sql
-- Spotify peut renvoyer des dates partielles ("2021", "2021-06").
-- On normalise en complétant avec le premier jour du mois/année si nécessaire.

with source as (
    select * from {{ source('lake', 'artists_albums') }}
),

data as (
    select
        spotify_id                          as album_id,
        trim(name)                          as nom,
        image_url                           as url_jaquette,
        artist_id                           as artiste_id,

        -- normalisation de la date selon sa longueur
        case
            when length(release_date) = 4
                then cast(release_date || '-01-01' as date)   -- "2021" → "2021-01-01"
            when length(release_date) = 7
                then cast(release_date || '-01' as date)      -- "2021-06" → "2021-06-01"
            when length(release_date) = 10
                then cast(release_date as date)               -- "2021-06-15" → ok
            else null
        end                                 as date_sortie

    from source

    where
        spotify_id is not null
        and trim(name) != ''
)

select * from data