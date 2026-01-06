"""
Base model for SQLAlchemy models in the backend service.

This module defines the base class for all SQLAlchemy models,
providing common functionality and shared attributes.
"""
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid


class BaseMixin:
    """
    Base mixin class for all SQLAlchemy models in the application.

    Provides common functionality and shared attributes for all models.
    """
    # Common ID field for all models
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Common timestamps for all models
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        """
        String representation of the model instance.

        Returns:
            str: String representation showing the model type and ID
        """
        return f"<{self.__class__.__name__}(id={self.id})>"