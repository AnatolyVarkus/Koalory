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
    story_location: Mapped[str] = mapped_column(nullable=True)
    story_extra: Mapped[str] = mapped_column(nullable=True)
    story_theme: Mapped[str] = mapped_column(String(255), nullable=True)
    story_message: Mapped[str] = mapped_column(nullable=True)
    story_language: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(default="not_started", nullable=True)
    error_message: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    photo_url: Mapped[str] = mapped_column(nullable=True)
    story_title: Mapped[str] = mapped_column(nullable=True)
    story_text: Mapped[str] = mapped_column(nullable=True)
    illustration_1: Mapped[str] = mapped_column(nullable=True)
    illustration_2: Mapped[str] = mapped_column(nullable=True)
    illustration_3: Mapped[str] = mapped_column(nullable=True)
    illustration_4: Mapped[str] = mapped_column(nullable=True)
    illustration_5: Mapped[str] = mapped_column(nullable=True)
    illustration_6: Mapped[str] = mapped_column(nullable=True)
    story_url: Mapped[str] = mapped_column(nullable=True)
    story_creation_ts: Mapped[int] = mapped_column(nullable=True)

    user = relationship("UsersModel", back_populates="stories")
