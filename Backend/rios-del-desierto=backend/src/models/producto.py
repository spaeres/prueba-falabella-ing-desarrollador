# src/models/producto.py
import uuid

from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Float, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.extensions import db

if TYPE_CHECKING:
    from src.models.detalle_compra import DetalleCompra


class Producto(db.Model):
    __tablename__ = "productos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Backref a detalles (un producto puede estar en muchos detalles)
    detalles_compra: Mapped[List["DetalleCompra"]] = relationship(
        "DetalleCompra",
        back_populates="producto",
        cascade="save-update, merge",
    )

    __table_args__ = (
        CheckConstraint("length(nombre) > 0", name="ck_producto_nombre_no_vacio"),
        CheckConstraint("precio >= 0", name="ck_producto_precio_no_negativo"),
    )
