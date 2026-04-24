with titres as (
    select 
        titre_id, 
        artiste_id,
        libelle,
        duree,
        url_ecoute,
        date_creation,        
        album,
        url_jaquette,
        date_sortie,
        style
    from {{ ref('int_titres_enrichis') }} 
    )

select * from titres