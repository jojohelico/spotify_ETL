with artistes as (
    select
        stg_a.artiste_id,
        stg_a.nom,
        count(distinct stg_t.titre_id) as nombre_titres,
        

    from {{ ref('stg_artistes') }} stg_a
    inner join {{ ref('stg_titres') }} stg_t on stg_a.artiste_id = stg_t.artiste_id
    group by stg_a.artiste_id, stg_a.nom
)

select * from artistes