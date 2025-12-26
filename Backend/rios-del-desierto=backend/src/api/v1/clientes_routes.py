from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from sqlalchemy import select
from io import BytesIO, StringIO
import pandas as pd
from openpyxl.utils import get_column_letter

from src.models.cliente import Cliente
from src.models.documento import Documento
from src.models.enums import TipoDocumentoEnum
from src.extensions import db

bp = Blueprint("clientes", __name__)



@bp.post("/clientes")
def crear_cliente():
    """
    Crea un nuevo cliente con su documento.
    
    Body (JSON):
        nombre: Nombre del cliente (requerido)
        apellido: Apellido del cliente (requerido)
        correoElectronico: Correo electrónico (requerido, único)
        telefonoCelular: Teléfono celular (requerido)
        fechaNacimiento: Fecha de nacimiento (opcional, formato: YYYY-MM-DD)
        documento:
            tipoDocumento: Tipo de documento (NIT, CEDULA, PASAPORTE) (requerido)
            numeroDocumento: Número del documento (requerido)
    
    Returns:
        201: Cliente creado exitosamente
        400: Datos inválidos o faltantes
        409: Cliente o documento ya existe
        500: Error al crear el cliente
    """
    try:
        # Obtener datos del request
        if not request.is_json:
            return jsonify({"error": "Content-Type debe ser application/json"}), 400
        
        data = request.get_json() or {}
        
        # Validar campos requeridos del cliente
        nombre = data.get("nombre")
        apellido = data.get("apellido")
        correo_electronico = data.get("correoElectronico") or data.get("correo_electronico")
        telefono_celular = data.get("telefonoCelular") or data.get("telefono_celular")
        fecha_nacimiento_str = data.get("fechaNacimiento") or data.get("fecha_nacimiento")
        
        # Validar campos requeridos
        if not nombre:
            return jsonify({"error": "El campo 'nombre' es requerido"}), 400
        if not apellido:
            return jsonify({"error": "El campo 'apellido' es requerido"}), 400
        if not correo_electronico:
            return jsonify({"error": "El campo 'correoElectronico' es requerido"}), 400
        if not telefono_celular:
            return jsonify({"error": "El campo 'telefonoCelular' es requerido"}), 400
        
        # Validar documento
        documento_data = data.get("documento") or {}
        tipo_documento_str = documento_data.get("tipoDocumento") or documento_data.get("tipo_documento")
        numero_documento = documento_data.get("numeroDocumento") or documento_data.get("numero_documento")
        
        if not tipo_documento_str:
            return jsonify({"error": "El campo 'documento.tipoDocumento' es requerido"}), 400
        if not numero_documento:
            return jsonify({"error": "El campo 'documento.numeroDocumento' es requerido"}), 400
        
        # Validar tipo de documento
        try:
            tipo_documento = TipoDocumentoEnum(tipo_documento_str.upper())
        except ValueError:
            valores_validos = [e.value for e in TipoDocumentoEnum]
            return jsonify({
                "error": f"Tipo de documento inválido. Valores válidos: {', '.join(valores_validos)}"
            }), 400
        
        # Validar que el correo no exista
        existing_cliente = db.session.scalar(
            select(Cliente).where(Cliente.correo_electronico == correo_electronico.strip().lower())
        )
        if existing_cliente:
            return jsonify({
                "error": f"Ya existe un cliente con el correo electrónico '{correo_electronico}'"
            }), 409
        
        # Validar que el documento no exista
        existing_documento = db.session.scalar(
            select(Documento).where(
                Documento.tipo_documento == tipo_documento,
                Documento.numero_documento == numero_documento.strip()
            )
        )
        if existing_documento:
            return jsonify({
                "error": f"Ya existe un documento con tipo '{tipo_documento.value}' y número '{numero_documento}'"
            }), 409
        
        # Parsear fecha de nacimiento si existe
        fecha_nacimiento = None
        if fecha_nacimiento_str:
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({
                    "error": "Formato de fecha inválido. Use YYYY-MM-DD"
                }), 400
        
        # Crear el cliente
        cliente = Cliente(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            correo_electronico=correo_electronico.strip().lower(),
            telefono_celular=telefono_celular.strip(),
            fecha_nacimiento=fecha_nacimiento
        )
        
        # Crear el documento
        documento = Documento(
            tipo_documento=tipo_documento,
            numero_documento=numero_documento.strip(),
            cliente=cliente
        )
        
        # Guardar en la base de datos
        db.session.add(cliente)
        db.session.add(documento)
        db.session.commit()
        
        # Preparar respuesta
        response = cliente.to_dict()
        response["documento"] = {
            "tipoDocumento": documento.tipo_documento.value,
            "numeroDocumento": documento.numero_documento
        }
        
        return jsonify(response), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al crear el cliente",
            "message": str(e)
        }), 500


@bp.route("/clientes/buscar", methods=["GET", "POST"])
def buscar_cliente_por_documento():
    """
    Busca un cliente por su tipo y número de documento.
    
    Acepta datos desde:
        - GET: Query parameters (?tipo_documento=...&numero_documento=...)
        - POST: Form data (application/x-www-form-urlencoded)
        - POST: JSON (application/json)
    
    Parámetros:
        tipo_documento: Tipo de documento (NIT, CEDULA, PASAPORTE)
        numero_documento: Número del documento
    
    Returns:
        200: Cliente encontrado
        400: Parámetros inválidos o faltantes
        404: Cliente no encontrado
    """
    # Intentar obtener datos desde diferentes fuentes (prioridad: JSON > Form > Query params)
    # React normalmente envía JSON con Content-Type: application/json
    if request.is_json:
        data = request.get_json() or {}
        tipo_documento_str = data.get("tipo_documento") or data.get("tipoDocumento")
        numero_documento = data.get("numero_documento") or data.get("numeroDocumento")
    elif request.method == "POST" and request.form:
        # Form data (formulario HTML tradicional)
        tipo_documento_str = request.form.get("tipo_documento") or request.form.get("tipoDocumento")
        numero_documento = request.form.get("numero_documento") or request.form.get("numeroDocumento")
    else:
        # GET: Query parameters
        tipo_documento_str = request.args.get("tipo_documento")
        numero_documento = request.args.get("numero_documento")
    
    # Validar que los parámetros estén presentes
    if not tipo_documento_str:
        return jsonify({"error": "El parámetro 'tipo_documento' es requerido"}), 400
    
    if not numero_documento:
        return jsonify({"error": "El parámetro 'numero_documento' es requerido"}), 400
    
    # Validar que el tipo de documento sea válido
    try:
        tipo_documento = TipoDocumentoEnum(tipo_documento_str.upper())
    except ValueError:
        valores_validos = [e.value for e in TipoDocumentoEnum]
        return jsonify({
            "error": f"Tipo de documento inválido. Valores válidos: {', '.join(valores_validos)}"
        }), 400
    
    # Buscar el cliente
    cliente = Cliente.buscar_por_documento(tipo_documento, numero_documento.strip())
    
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404
    
    # Retornar el cliente con su documento
    response = cliente.to_dict()
    if cliente.documento:
        response["documento"] = {
            "tipoDocumento": cliente.documento.tipo_documento.value,
            "numeroDocumento": cliente.documento.numero_documento
        }
    
    return jsonify(response), 200


@bp.route("/clientes/exportar", methods=["GET", "POST"])
def exportar_cliente():
    """
    Exporta la información de un cliente en diferentes formatos (CSV, TXT, Excel).
    
    Query parameters:
        tipo_documento: Tipo de documento (NIT, CEDULA, PASAPORTE) (requerido)
        numero_documento: Número del documento (requerido)
        formato: Formato de exportación - CSV, TXT o Excel (requerido)
    
    También acepta POST con JSON o form data (igual que el endpoint de búsqueda).
    
    Returns:
        200: Archivo descargable con la información del cliente
        400: Parámetros inválidos o faltantes
        404: Cliente no encontrado
    """
    try:
        # Obtener parámetros de búsqueda (misma lógica que buscar_cliente_por_documento)
        if request.is_json:
            data = request.get_json() or {}
            tipo_documento_str = data.get("tipo_documento") or data.get("tipoDocumento")
            numero_documento = data.get("numero_documento") or data.get("numeroDocumento")
        elif request.method == "POST" and request.form:
            tipo_documento_str = request.form.get("tipo_documento") or request.form.get("tipoDocumento")
            numero_documento = request.form.get("numero_documento") or request.form.get("numeroDocumento")
        else:
            tipo_documento_str = request.args.get("tipo_documento")
            numero_documento = request.args.get("numero_documento")
        
        # Obtener formato de exportación
        formato = request.args.get("formato") or request.form.get("formato")
        if request.is_json:
            data = request.get_json() or {}
            formato = formato or data.get("formato")
        
        # Validar parámetros requeridos
        if not tipo_documento_str:
            return jsonify({"error": "El parámetro 'tipo_documento' es requerido"}), 400
        
        if not numero_documento:
            return jsonify({"error": "El parámetro 'numero_documento' es requerido"}), 400
        
        if not formato:
            return jsonify({"error": "El parámetro 'formato' es requerido. Valores válidos: CSV, TXT, Excel"}), 400
        
        # Validar formato
        formato = formato.upper()
        if formato not in ["CSV", "TXT", "EXCEL"]:
            return jsonify({
                "error": f"Formato inválido. Valores válidos: CSV, TXT, Excel"
            }), 400
        
        # Validar tipo de documento
        try:
            tipo_documento = TipoDocumentoEnum(tipo_documento_str.upper())
        except ValueError:
            valores_validos = [e.value for e in TipoDocumentoEnum]
            return jsonify({
                "error": f"Tipo de documento inválido. Valores válidos: {', '.join(valores_validos)}"
            }), 400
        
        # Buscar el cliente
        cliente = Cliente.buscar_por_documento(tipo_documento, numero_documento.strip())
        
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404
        
        # Preparar datos del cliente
        datos_cliente = {
            "ID": str(cliente.id),
            "Nombre": cliente.nombre,
            "Apellido": cliente.apellido,
            "Correo Electrónico": cliente.correo_electronico,
            "Teléfono Celular": cliente.telefono_celular,
            "Fecha de Nacimiento": cliente.fecha_nacimiento.isoformat() if cliente.fecha_nacimiento else "N/A",
            "Tipo Documento": cliente.documento.tipo_documento.value if cliente.documento else "N/A",
            "Número Documento": cliente.documento.numero_documento if cliente.documento else "N/A",
            "Fecha Creación": cliente.created_at.isoformat() if cliente.created_at else "N/A",
            "Fecha Actualización": cliente.updated_at.isoformat() if cliente.updated_at else "N/A"
        }
        
        # Generar archivo según el formato
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_base = f"cliente_{cliente.nombre}_{cliente.apellido}_{fecha_str}"
        
        if formato == "CSV":
            # Generar CSV
            df = pd.DataFrame([datos_cliente])
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"{nombre_base}.csv"
            )
        
        elif formato == "TXT":
            # Generar TXT
            output = StringIO()
            output.write("=" * 50 + "\n")
            output.write("INFORMACIÓN DEL CLIENTE\n")
            output.write("=" * 50 + "\n\n")
            
            for clave, valor in datos_cliente.items():
                output.write(f"{clave}: {valor}\n")
            
            output.write("\n" + "=" * 50 + "\n")
            output.seek(0)
            
            txt_bytes = BytesIO(output.getvalue().encode('utf-8'))
            
            return send_file(
                txt_bytes,
                mimetype='text/plain',
                as_attachment=True,
                download_name=f"{nombre_base}.txt"
            )
        
        elif formato == "EXCEL":
            # Generar Excel
            df = pd.DataFrame([datos_cliente])
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Información Cliente', index=False)
                
                # Formatear la hoja
                worksheet = writer.sheets['Información Cliente']
                
                # Ajustar ancho de columnas
                for idx, col in enumerate(df.columns, 1):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    col_letter = get_column_letter(idx)
                    worksheet.column_dimensions[col_letter].width = min(max_length, 50)
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{nombre_base}.xlsx"
            )
        
    except Exception as e:
        return jsonify({
            "error": "Error al exportar la información del cliente",
            "message": str(e)
        }), 500

