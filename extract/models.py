from datetime import datetime
 
from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
 
 
class Base(DeclarativeBase):
    pass
 
 
class Artist(Base):
    __tablename__ = "artists_search"
    __table_args__ = {"schema": "lake"}
 
    spotify_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    genres: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_genre: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    spotify_url: Mapped[str | None] = mapped_column(Text, nullable=True)


    albums: Mapped[list["Album"]] = relationship(back_populates="artist")
 
class Album(Base):
    __tablename__ = "artists_albums"
    __table_args__ = {"schema": "lake"}
 
    spotify_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    release_date: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    artist_id: Mapped[str] = mapped_column(
    Text, ForeignKey("lake.artists_search.spotify_id"), nullable=False
)
    total_tracks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    album_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    spotify_url: Mapped[str | None] = mapped_column(Text, nullable=True)
 
    artist: Mapped["Artist"] = relationship(back_populates="albums")
    titres: Mapped[list["Titre"]] = relationship(back_populates="album")

class Titre(Base):
    __tablename__ = "titres"
    __table_args__ = {"schema": "lake"}
 
    spotify_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    track_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    album_id: Mapped[str] = mapped_column(
    Text, ForeignKey("lake.artists_albums.spotify_id"), nullable=False
)
    spotify_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    is_playable: Mapped[bool | None] = mapped_column(nullable=True)
    explicit: Mapped[bool | None] = mapped_column(nullable=True)

    album: Mapped["Album"] = relationship(back_populates="titres")