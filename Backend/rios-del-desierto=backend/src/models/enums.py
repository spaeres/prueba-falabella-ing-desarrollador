# src/models/enums.py
import enum


class TipoDocumentoEnum(str, enum.Enum):
    NIT = "NIT"
    CEDULA = "CEDULA"
    PASAPORTE = "PASAPORTE"


class EstadoCompraEnum(str, enum.Enum):
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
    REEMBOLSADA = "REEMBOLSADA"
