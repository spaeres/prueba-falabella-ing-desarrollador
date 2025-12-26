import React, { useState } from "react";
import ExportModal from "./ExportModal";

export default function ClientDetails({ client }) {
  const [showExport, setShowExport] = useState(false);

  if (!client) return null;

  return (
    <div className="card mt-3">
      <div className="card-body">
        <h5 className="card-title">Datos del cliente</h5>

        <div className="row">
          <div className="col-sm-6">
            <strong>Tipo doc:</strong> {client.tipo_documento || "-"}
          </div>
          <div className="col-sm-6">
            <strong>Número de documento:</strong>{" "}
            {client.numero_documento || "-"}
          </div>
          <div className="col-sm-6">
            <strong>Nombre:</strong> {client.nombre || "-"}
          </div>
          <div className="col-sm-6">
            <strong>Apellido:</strong> {client.apellido || "-"}
          </div>
          <div className="col-sm-6">
            <strong>Correo:</strong> {client.correo || "-"}
          </div>
          <div className="col-sm-6">
            <strong>Teléfono:</strong> {client.telefono || "-"}
          </div>
        </div>

        <div className="mt-3">
          <button
            className="btn btn-outline-secondary"
            onClick={() => setShowExport(true)}
          >
            Descargar datos
          </button>
        </div>
      </div>

      <ExportModal
        show={showExport}
        onClose={() => setShowExport(false)}
        cliente={client}
      />
    </div>
  );
}
