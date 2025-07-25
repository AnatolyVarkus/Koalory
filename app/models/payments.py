from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class PaymentsModel(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    bundle_name: Mapped[str] = mapped_column(String(255))
    available_stories: Mapped[int] = mapped_column()
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("UsersModel", back_populates="payments")
