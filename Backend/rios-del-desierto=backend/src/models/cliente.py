# src/models/cliente.py
import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import select, func

from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from sqlalchemy import String, Date, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.extensions import db
from .enums import TipoDocumentoEnum

if TYPE_CHECKING:
    from src.models.compra import Compra


class Cliente(db.Model):
    __tablename__ = "clientes"

    # PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Datos básicos
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    apellido: Mapped[str] = mapped_column(String(80), nullable=False)

    correo_electronico: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
        index=True
    )

    telefono_celular: Mapped[str] = mapped_column(String(30), nullable=False)

    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relaciones con otras tablas:
    documento = relationship(
        "Documento",
        back_populates="cliente",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
        passive_deletes=True,
    )

    compras: Mapped[List["Compra"]] = relationship(
        "Compra",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # Constraints de la tabla clientes:
    __table_args__ = (
        # Strings no vacíos
        CheckConstraint("length(nombre) > 0", name="ck_cliente_nombre_no_vacio"),
        CheckConstraint("length(apellido) > 0", name="ck_cliente_apellido_no_vacio"),
        CheckConstraint(
            "length(correo_electronico) > 0",
            name="ck_cliente_correo_no_vacio"
        ),
        CheckConstraint(
            "length(telefono_celular) > 0",
            name="ck_cliente_telefono_no_vacio"
        ),

        # Fecha de nacimiento no futura (si existe)
        CheckConstraint(
            "fecha_nacimiento IS NULL OR fecha_nacimiento <= DATE('now')",
            name="ck_cliente_fecha_nacimiento_valida"
        ),
    )

    # --------------------
    # Validaciones simples
    # --------------------
    @validates("correo_electronico")
    def validate_email(self, key, value: str):
        value = (value or "").strip().lower()
        if "@" not in value:
            raise ValueError("correo_electronico inválido")
        return value

    @validates("nombre", "apellido", "telefono_celular")
    def validate_non_empty(self, key, value: str):
        value = (value or "").strip()
        if not value:
            raise ValueError(f"{key} no puede estar vacío")
        return value

    @validates("fecha_nacimiento")
    def validate_birthdate(self, key, value):
        if value is None:
            return None
        if value > date.today():
            raise ValueError("fecha_nacimiento no puede ser futura")
        return value

    def to_dict(self):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correoElectronico": self.correo_electronico,
            "telefonoCelular": self.telefono_celular,
            "fechaNacimiento": self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
        }

    @classmethod
    def buscar_por_documento(cls, tipo_documento: TipoDocumentoEnum, numero_documento: str) -> Optional["Cliente"]:
        """
        Busca un cliente por su tipo y número de documento.
        
        Args:
            tipo_documento: Tipo de documento (NIT, CEDULA, PASAPORTE)
            numero_documento: Número del documento
            
        Returns:
            Cliente si se encuentra, None si no existe
        """
        from .documento import Documento
        
        documento = db.session.query(Documento).filter(
            Documento.tipo_documento == tipo_documento,
            Documento.numero_documento == numero_documento
        ).first()
        
        if documento:
            return documento.cliente
        return None

    def calcular_total_compras_ultimo_mes(self) -> float:
        """
        Calcula el monto total de compras del cliente en el último mes (últimos 30 días).
        
        Returns:
            Monto total de compras del último mes
        """
        from .compra import Compra
        from .enums import EstadoCompraEnum
        
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        
        stmt = select(func.coalesce(func.sum(Compra.monto_total), 0)).where(
            Compra.cliente_id == self.id,
            Compra.fecha >= fecha_limite,
            Compra.status == EstadoCompraEnum.COMPLETADA
        )
        
        total = db.session.scalar(stmt) or 0.0
        return float(total)

    @classmethod
    def obtener_clientes_fidelizacion(cls, monto_minimo: float = 5_000_000) -> List["Cliente"]:
        """
        Obtiene los clientes que superan el monto mínimo de compras en el último mes.
        
        Args:
            monto_minimo: Monto mínimo en COP (por defecto 5'000.000)
            
        Returns:
            Lista de clientes que superan el monto mínimo en el último mes
        """
        from .compra import Compra
        from .enums import EstadoCompraEnum
        
        fecha_limite = datetime.utcnow() - timedelta(days=30)
        
        # Subconsulta para obtener el total por cliente
        subquery = select(
            Compra.cliente_id,
            func.sum(Compra.monto_total).label('total')
        ).where(
            Compra.fecha >= fecha_limite,
            Compra.status == EstadoCompraEnum.COMPLETADA
        ).group_by(Compra.cliente_id).having(
            func.sum(Compra.monto_total) > monto_minimo
        ).subquery()
        
        # Obtener los clientes que cumplen la condición
        stmt = select(cls).join(
            subquery, cls.id == subquery.c.cliente_id
        )
        
        return list(db.session.scalars(stmt).all())
