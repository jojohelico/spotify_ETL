import logging
from datetime import datetime

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from extract.models import Base


class LoaderService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.EXCLUDED_FROM_UPDATE = {"spotify_id", "extracted_at"}

    def _ensure_schema(self, engine) -> None:
        """Crée le schéma lake et les tables si ils n'existent pas encore."""
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS lake"))
            conn.commit()
        Base.metadata.create_all(engine)

    def load(self, items: list[Base], engine) -> None:
        if not items:
            self.logger.warning("Aucun élément à charger.")
            return

        items = list({getattr(i, 'spotify_id'): i for i in items}.values())

        model = type(items[0])
        # récupère toutes les colonnes du modèle via SQLAlchemy inspect
        columns = [c.key for c in inspect(model).mapper.column_attrs]

        rows = [
            {**{col: getattr(item, col) for col in columns}, "extracted_at": datetime.now()}
            for item in items
        ]

        # colonnes à mettre à jour = toutes sauf la PK et extracted_at
        update_cols = [c for c in columns if c not in self.EXCLUDED_FROM_UPDATE]

        stmt = insert(model).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["spotify_id"],
            set_={col: getattr(stmt.excluded, col) for col in update_cols},
        )

        with Session(engine) as session:
            session.execute(stmt)
            session.commit()

        self.logger.info(
            "%d %s chargés.", len(items), model.__tablename__
        )