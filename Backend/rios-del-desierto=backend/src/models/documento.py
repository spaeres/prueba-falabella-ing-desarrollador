import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint, String, CheckConstraint
from .enums import TipoDocumentoEnum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.extensions import db


if TYPE_CHECKING:
    from .cliente import Cliente


class Documento(db.Model):
    __tablename__ = "documentos"

    # PK
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    numero_documento: Mapped[str] = mapped_column(String(40), nullable=False)
    tipo_documento: Mapped[TipoDocumentoEnum] = mapped_column(
        Enum(TipoDocumentoEnum, name="tipo_documento_enum", native_enum=False),
        nullable=False,
    )

    # 1–1 con Cliente (composición): Documento depende de Cliente
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        db.Uuid,
        ForeignKey("clientes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # fuerza 1–1 (un documento por cliente)
    )

    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        back_populates="documento",
        uselist=False,
    )

    __table_args__ = (
        # No vacíos
        CheckConstraint("length(numero_documento) > 0", name="ck_doc_numero_no_vacio"),
        # Búsqueda principal: tipo + numero únicos
        UniqueConstraint("tipo_documento", "numero_documento", name="uq_doc_tipo_numero"),
    )
