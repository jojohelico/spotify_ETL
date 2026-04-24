with artistes as (
    select * from {{ ref('stg_artistes') }}
),

titres as (
    select * from {{ ref('int_titres_enrichis') }}
),

albums as (
    select * from {{ ref('stg_albums') }}
),

-- artiste avec le plus de titres
artiste_le_plus_chronique as (
    select
        artiste_id,
        nom_artiste,
        count(*) as nb_titres
    from titres
    group by artiste_id, nom_artiste
    order by nb_titres desc
    limit 1
),

-- album avec le plus de titres
album_le_plus_chronique as (
    select
        album_id,
        album,
        count(*) as nb_titres
    from titres
    group by album_id, album
    order by nb_titres desc
    limit 1
),

final as (
    select
        (select count(distinct artiste_id) from artistes)           as "NombreArtistes",
        (select count(distinct titre_id) from titres)               as "NombreTitres",
        (select count(distinct style) from artistes)                as "NombreGenres",
        (select nom_artiste from artiste_le_plus_chronique)         as "ArtisteLePlusChronique",
        (select album from album_le_plus_chronique)                 as "AlbumLePlusChronique"
)

select * from final