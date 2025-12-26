# src/db/seed.py
from datetime import datetime, timedelta, date
import uuid

from src.extensions import db
from src.models.cliente import Cliente
from src.models.documento import Documento
from src.models.producto import Producto
from src.models.compra import Compra
from src.models.detalle_compra import DetalleCompra
from src.models.enums import TipoDocumentoEnum, EstadoCompraEnum


def run_seed():
    print("Iniciando seed de base de datos...")

    # Evita duplicar seed
    from sqlalchemy import select
    existing_cliente = db.session.scalar(select(Cliente).limit(1))
    if existing_cliente:
        print("Ya existen datos. Seed omitido.")
        return

    # -------------------
    # Cliente + Documento
    # -------------------
    cliente = Cliente(
        nombre="Juan",
        apellido="Pérez",
        correo_electronico="juan.perez@example.com",
        telefono_celular="3001234567",
        fecha_nacimiento=date(1990, 5, 20),
    )

    documento = Documento(
        tipo_documento=TipoDocumentoEnum.CEDULA,
        numero_documento="123456789",
        cliente=cliente,
    )

    # ----------
    # Productos
    # ----------
    producto_1 = Producto(nombre="Televisor 65 pulgadas", precio=3_000_000)
    producto_2 = Producto(nombre="Portátil Gamer", precio=2_500_000)
    producto_3 = Producto(nombre="Barra de Sonido", precio=600_000)

    # -------------------------
    # Compra del último mes (>5M)
    # -------------------------
    compra_reciente = Compra(
        fecha=datetime.utcnow() - timedelta(days=10),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente,
    )

    detalle_1 = DetalleCompra(
        producto=producto_1,
        cantidad_compra=1,
        precio_unitario=producto_1.precio,
        compra=compra_reciente,
    )

    detalle_2 = DetalleCompra(
        producto=producto_2,
        cantidad_compra=1,
        precio_unitario=producto_2.precio,
        compra=compra_reciente,
    )

    compra_reciente.monto_total = (
        detalle_1.cantidad_compra * detalle_1.precio_unitario +
        detalle_2.cantidad_compra * detalle_2.precio_unitario
    )

    # -------------------------
    # Compra antigua (no cuenta)
    # -------------------------
    compra_antigua = Compra(
        fecha=datetime.utcnow() - timedelta(days=120),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente,
    )

    detalle_3 = DetalleCompra(
        producto=producto_3,
        cantidad_compra=1,
        precio_unitario=producto_3.precio,
        compra=compra_antigua,
    )

    compra_antigua.monto_total = (
        detalle_3.cantidad_compra * detalle_3.precio_unitario
    )

    # -------------------------
    # María González + Documento
    # -------------------------
    cliente_maria = Cliente(
        nombre="María",
        apellido="González",
        correo_electronico="maria.gonzalez@example.com",
        telefono_celular="3009876543",
        fecha_nacimiento=date(1995, 3, 15),
    )

    documento_maria = Documento(
        tipo_documento=TipoDocumentoEnum.CEDULA,
        numero_documento="987654321",
        cliente=cliente_maria,
    )

    # -------------------------
    # Compras de María González
    # -------------------------
    # Compra 1: Del último mes que supera 5,500,000 (6,100,000)
    compra_maria_1 = Compra(
        fecha=datetime.utcnow() - timedelta(days=5),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_maria,
    )

    detalle_maria_1_1 = DetalleCompra(
        producto=producto_1,  # Televisor: 3,000,000
        cantidad_compra=1,
        precio_unitario=producto_1.precio,
        compra=compra_maria_1,
    )

    detalle_maria_1_2 = DetalleCompra(
        producto=producto_2,  # Portátil: 2,500,000
        cantidad_compra=1,
        precio_unitario=producto_2.precio,
        compra=compra_maria_1,
    )

    detalle_maria_1_3 = DetalleCompra(
        producto=producto_3,  # Barra de Sonido: 600,000
        cantidad_compra=1,
        precio_unitario=producto_3.precio,
        compra=compra_maria_1,
    )

    compra_maria_1.monto_total = (
        detalle_maria_1_1.cantidad_compra * detalle_maria_1_1.precio_unitario +
        detalle_maria_1_2.cantidad_compra * detalle_maria_1_2.precio_unitario +
        detalle_maria_1_3.cantidad_compra * detalle_maria_1_3.precio_unitario
    )  # Total: 6,100,000

    # Compra 2: Del último mes pero NO supera 5,500,000 (3,000,000)
    compra_maria_2 = Compra(
        fecha=datetime.utcnow() - timedelta(days=15),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_maria,
    )

    detalle_maria_2_1 = DetalleCompra(
        producto=producto_1,  # Televisor: 3,000,000
        cantidad_compra=1,
        precio_unitario=producto_1.precio,
        compra=compra_maria_2,
    )

    compra_maria_2.monto_total = (
        detalle_maria_2_1.cantidad_compra * detalle_maria_2_1.precio_unitario
    )  # Total: 3,000,000

    # Compra 3: Del último mes pequeña (600,000)
    compra_maria_3 = Compra(
        fecha=datetime.utcnow() - timedelta(days=20),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_maria,
    )

    detalle_maria_3_1 = DetalleCompra(
        producto=producto_3,  # Barra de Sonido: 600,000
        cantidad_compra=1,
        precio_unitario=producto_3.precio,
        compra=compra_maria_3,
    )

    compra_maria_3.monto_total = (
        detalle_maria_3_1.cantidad_compra * detalle_maria_3_1.precio_unitario
    )  # Total: 600,000

    # -------------------------
    # Pedro Martínez + Documento
    # -------------------------
    cliente_pedro = Cliente(
        nombre="Pedro",
        apellido="Martínez",
        correo_electronico="pedro.martinez@example.com",
        telefono_celular="3005551234",
        fecha_nacimiento=date(1988, 7, 22),
    )

    documento_pedro = Documento(
        tipo_documento=TipoDocumentoEnum.CEDULA,
        numero_documento="456789123",
        cliente=cliente_pedro,
    )

    # -------------------------
    # Compras de Pedro Martínez (NO superan 5,500,000 este mes)
    # -------------------------
    # Compra 1: Del último mes (2,500,000)
    compra_pedro_1 = Compra(
        fecha=datetime.utcnow() - timedelta(days=8),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_pedro,
    )

    detalle_pedro_1_1 = DetalleCompra(
        producto=producto_2,  # Portátil: 2,500,000
        cantidad_compra=1,
        precio_unitario=producto_2.precio,
        compra=compra_pedro_1,
    )

    compra_pedro_1.monto_total = (
        detalle_pedro_1_1.cantidad_compra * detalle_pedro_1_1.precio_unitario
    )  # Total: 2,500,000

    # Compra 2: Del último mes (3,000,000)
    compra_pedro_2 = Compra(
        fecha=datetime.utcnow() - timedelta(days=12),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_pedro,
    )

    detalle_pedro_2_1 = DetalleCompra(
        producto=producto_1,  # Televisor: 3,000,000
        cantidad_compra=1,
        precio_unitario=producto_1.precio,
        compra=compra_pedro_2,
    )

    compra_pedro_2.monto_total = (
        detalle_pedro_2_1.cantidad_compra * detalle_pedro_2_1.precio_unitario
    )  # Total: 3,000,000
    
    # Compra 3: Del último mes pequeña (600,000)
    compra_pedro_3 = Compra(
        fecha=datetime.utcnow() - timedelta(days=18),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_pedro,
    )

    detalle_pedro_3_1 = DetalleCompra(
        producto=producto_3,  # Barra de Sonido: 600,000
        cantidad_compra=1,
        precio_unitario=producto_3.precio,
        compra=compra_pedro_3,
    )

    compra_pedro_3.monto_total = (
        detalle_pedro_3_1.cantidad_compra * detalle_pedro_3_1.precio_unitario
    )  # Total: 600,000
    # Total de Pedro este mes: 2,500,000 + 3,000,000 + 600,000 = 6,100,000
    
    # Ajustar compra_pedro_2 para que el total NO supere 5,000,000
    # Cambiar el precio unitario a 2,000,000 (simulando un descuento)
    detalle_pedro_2_1.precio_unitario = 1_000_000.0
    compra_pedro_2.monto_total = 1_000_000.0
    # Total de Pedro este mes: 2,500,000 + 1,000,000 + 600,000 = 4,100,000 (NO supera 5,000,000)

    # -------------------------
    # Cliente con PASAPORTE
    # -------------------------
    cliente_pasaporte = Cliente(
        nombre="Ana",
        apellido="Rodríguez",
        correo_electronico="ana.rodriguez@example.com",
        telefono_celular="3007778888",
        fecha_nacimiento=date(1992, 11, 8),
    )

    documento_pasaporte = Documento(
        tipo_documento=TipoDocumentoEnum.PASAPORTE,
        numero_documento="AB123456",
        cliente=cliente_pasaporte,
    )

    # Compra del cliente con pasaporte
    compra_pasaporte = Compra(
        fecha=datetime.utcnow() - timedelta(days=7),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_pasaporte,
    )

    detalle_pasaporte = DetalleCompra(
        producto=producto_2,  # Portátil: 2,500,000
        cantidad_compra=1,
        precio_unitario=producto_2.precio,
        compra=compra_pasaporte,
    )

    compra_pasaporte.monto_total = (
        detalle_pasaporte.cantidad_compra * detalle_pasaporte.precio_unitario
    )  # Total: 2,500,000

    # -------------------------
    # Cliente con NIT
    # -------------------------
    cliente_nit = Cliente(
        nombre="Empresa",
        apellido="Comercial S.A.S.",
        correo_electronico="contacto@empresacomercial.com",
        telefono_celular="6012345678",
        fecha_nacimiento=None,  # Las empresas no tienen fecha de nacimiento
    )

    documento_nit = Documento(
        tipo_documento=TipoDocumentoEnum.NIT,
        numero_documento="900123456-7",
        cliente=cliente_nit,
    )

    # Compra del cliente con NIT (compra grande)
    compra_nit = Compra(
        fecha=datetime.utcnow() - timedelta(days=3),
        status=EstadoCompraEnum.COMPLETADA,
        cliente=cliente_nit,
    )

    detalle_nit_1 = DetalleCompra(
        producto=producto_1,  # Televisor: 3,000,000
        cantidad_compra=2,
        precio_unitario=producto_1.precio,
        compra=compra_nit,
    )

    detalle_nit_2 = DetalleCompra(
        producto=producto_2,  # Portátil: 2,500,000
        cantidad_compra=1,
        precio_unitario=producto_2.precio,
        compra=compra_nit,
    )

    compra_nit.monto_total = (
        detalle_nit_1.cantidad_compra * detalle_nit_1.precio_unitario +
        detalle_nit_2.cantidad_compra * detalle_nit_2.precio_unitario
    )  # Total: 8,500,000

    # -------------------------
    # Persistir todo
    # -------------------------
    db.session.add_all([
        cliente,
        documento,
        producto_1,
        producto_2,
        producto_3,
        compra_reciente,
        compra_antigua,
        # María González
        cliente_maria,
        documento_maria,
        compra_maria_1,
        detalle_maria_1_1,
        detalle_maria_1_2,
        detalle_maria_1_3,
        compra_maria_2,
        detalle_maria_2_1,
        compra_maria_3,
        detalle_maria_3_1,
        # Pedro Martínez
        cliente_pedro,
        documento_pedro,
        compra_pedro_1,
        detalle_pedro_1_1,
        compra_pedro_2,
        detalle_pedro_2_1,
        compra_pedro_3,
        detalle_pedro_3_1,
        # Cliente con PASAPORTE
        cliente_pasaporte,
        documento_pasaporte,
        compra_pasaporte,
        detalle_pasaporte,
        # Cliente con NIT
        cliente_nit,
        documento_nit,
        compra_nit,
        detalle_nit_1,
        detalle_nit_2,
    ])

    db.session.commit()

    print("Seed completado correctamente.")
