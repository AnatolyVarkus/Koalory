from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class StoriesModel(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    story_name: Mapped[str] = mapped_column(String(255), nullable=True)
    story_age: Mapped[int] = mapped_column(nullable=True)
    story_gender: Mapped[str] = mapped_column(String(255), nullable=True)
    story_location: Mapped[str] = mapped_column(String(255), nullable=True)
    story_extra: Mapped[str] = mapped_column(String(255), nullable=True)
    story_theme: Mapped[str] = mapped_column(String(255), nullable=True)
    story_message: Mapped[str] = mapped_column(String(255), nullable=True)
    progress: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    photo_url: Mapped[str] = mapped_column(nullable=True)
    photo_creation_ts: Mapped[int] = mapped_column(nullable=True)
    story_url: Mapped[str] = mapped_column(nullable=True)
    story_creation_ts: Mapped[int] = mapped_column(nullable=True)


    user = relationship("UsersModel", back_populates="stories")
