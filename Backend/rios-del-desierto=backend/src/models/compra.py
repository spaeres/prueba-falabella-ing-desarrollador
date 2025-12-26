# src/models/compra.py
import uuid
from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING, Tuple

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Float, Enum, ForeignKey, CheckConstraint, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload

from src.extensions import db
from .enums import EstadoCompraEnum

if TYPE_CHECKING:
    from .detalle_compra import DetalleCompra


class Compra(db.Model):
    __tablename__ = "compras"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    monto_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    status: Mapped[EstadoCompraEnum] = mapped_column(
        Enum(EstadoCompraEnum, name="estado_compra_enum", native_enum=False),
        nullable=False,
        default=EstadoCompraEnum.COMPLETADA,
    )

    # FK a Cliente (asumiendo Cliente 1 -> 0..* Compra)
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        db.Uuid,
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cliente = relationship("Cliente", back_populates="compras")

    # Composición: Compra 1 -> 1..* DetalleCompra
    detalles_compra: Mapped[List["DetalleCompra"]] = relationship(
        "DetalleCompra",
        back_populates="compra",
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("monto_total > 0", name="ck_compra_monto_no_negativo_ni_cero"),
    )

    @classmethod
    def obtener_compras_mayores_a(cls, monto_minimo: float = 5_000_000) -> List["Compra"]:
        """
        Obtiene todas las compras cuyo monto_total es mayor al monto mínimo especificado.
        
        Args:
            monto_minimo: Monto mínimo en COP (por defecto 5'000.000)
            
        Returns:
            Lista de compras que superan el monto mínimo
        """
        stmt = select(cls).where(cls.monto_total > monto_minimo)
        return list(db.session.scalars(stmt).all())

    @classmethod
    def obtener_compras_ultimo_mes(cls) -> List["Compra"]:
        """
        Obtiene todas las compras del último mes (últimos 30 días).
        
        Returns:
            Lista de compras del último mes
        """
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        stmt = select(cls).where(cls.fecha >= fecha_limite)
        return list(db.session.scalars(stmt).all())

    @classmethod
    def obtener_compras_ultimo_mes_mayores_a(cls, monto_minimo: float = 5_000_000) -> List["Compra"]:
        """
        Obtiene todas las compras del último mes que superan el monto mínimo.
        
        Args:
            monto_minimo: Monto mínimo en COP (por defecto 5'000.000)
            
        Returns:
            Lista de compras del último mes que superan el monto mínimo
        """
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        stmt = select(cls).where(
            cls.fecha >= fecha_limite,
            cls.monto_total > monto_minimo
        )
        return list(db.session.scalars(stmt).all())

    @classmethod
    def obtener_detalles_compras_con_productos_ultimo_mes(
        cls, 
        monto_minimo_total: float = 5_000_000
    ) -> List:
        """
        Obtiene todos los detalles de compra con información de productos y compras
        para clientes que superan el monto mínimo en el último mes.
        
        Hace join de: Compra -> DetalleCompra -> Producto -> Cliente
        
        Args:
            monto_minimo_total: Monto mínimo total de compras del cliente en el último mes
            
        Returns:
            Lista de tuplas (Compra, DetalleCompra, Producto) con todos los detalles
        """
        from .detalle_compra import DetalleCompra
        from .producto import Producto
        from sqlalchemy import func
        
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        
        # Subconsulta para obtener clientes que cumplen el criterio
        subquery_clientes = select(
            Compra.cliente_id
        ).where(
            Compra.fecha >= fecha_limite,
            Compra.status == EstadoCompraEnum.COMPLETADA
        ).group_by(Compra.cliente_id).having(
            func.sum(Compra.monto_total) > monto_minimo_total
        ).subquery()
        
        # Query principal: obtener todas las compras de esos clientes con sus detalles y productos
        stmt = (
            select(Compra, DetalleCompra, Producto)
            .join(DetalleCompra, Compra.id == DetalleCompra.compra_id)
            .join(Producto, DetalleCompra.producto_id == Producto.id)
            .join(subquery_clientes, Compra.cliente_id == subquery_clientes.c.cliente_id)
            .where(
                Compra.fecha >= fecha_limite,
                Compra.status == EstadoCompraEnum.COMPLETADA
            )
            .order_by(Compra.fecha.desc(), Producto.nombre)
        )
        
        return list(db.session.execute(stmt).all())
