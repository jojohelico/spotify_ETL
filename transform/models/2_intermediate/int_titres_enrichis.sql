with titres as (
    select * from {{ ref('stg_titres') }}
),

albums as (
    select * from {{ ref('stg_albums') }}
),

artistes as (
    select * from {{ ref('stg_artistes') }}
),

enriched as (
    select
        -- identifiants
        titres.titre_id,
        titres.album_id,
        albums.artiste_id,

        -- champs titre
        titres.libelle,
        titres.duree,
        titres.url_ecoute,
        titres.track_number,
        titres.is_playable,
        titres.explicit,
        titres.date_creation,

        -- champs issus de l'album
        albums.nom          as album,
        albums.url_jaquette,
        albums.date_sortie,

        -- champs issus de l'artiste
        artistes.style,
        artistes.nom        as nom_artiste

    from titres

    inner join albums
        on titres.album_id = albums.album_id

    inner join artistes
        on albums.artiste_id = artistes.artiste_id

    where
        titres.is_playable = true   -- on n'importe que les titres disponibles à l'écoute

    order by titres.album_id, titres.track_number
)

select * from enriched