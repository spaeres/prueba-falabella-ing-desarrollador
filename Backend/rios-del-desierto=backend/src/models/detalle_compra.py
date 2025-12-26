# src/models/detalle_compra.py
import uuid
from typing import Optional

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Float, Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.extensions import db


class DetalleCompra(db.Model):
    __tablename__ = "detalles_compra"

    # PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    cantidad_compra: Mapped[int] = mapped_column(Integer, nullable=False)

    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)

    # FK a Compra (parte de la composición)
    compra_id: Mapped[uuid.UUID] = mapped_column(
        db.Uuid,
        ForeignKey("compras.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    compra = relationship("Compra", back_populates="detalles_compra")

    # FK a Producto (cada detalle referencia 1 producto)
    producto_id: Mapped[uuid.UUID] = mapped_column(
        db.Uuid,
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    producto = relationship("Producto", back_populates="detalles_compra")

    __table_args__ = (
        CheckConstraint("cantidad_compra > 0", name="ck_detalle_cantidad_mayor_que_cero"),
        CheckConstraint("precio_unitario >= 0", name="ck_detalle_precio_unitario_no_negativo"),
        # No puede estar repetido el mismo producto en el mismo detalle de la compra.
        # Para eso se usa el atributo cantidad:
        UniqueConstraint("compra_id", "producto_id", name="uq_detalle_compra_producto"),
    )
