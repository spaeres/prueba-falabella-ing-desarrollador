import React, { useState } from "react";
import { exportCliente } from "../utils/api";
import Loading from "./Loading";

export default function ExportModal({ show, onClose, cliente }) {
  const [formato, setFormato] = useState("EXCEL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!show) return null;

  async function handleConfirm() {
    if (!cliente) return;
    setLoading(true);
    setError(null);
    try {
      const blob = await exportCliente(
        cliente.tipo_documento,
        cliente.numero_documento || cliente.documento || cliente.id,
        formato
      );
      const ext =
        formato === "TXT" ? "txt" : formato === "CSV" ? "csv" : "xlsx";
      const filename = `cliente-${
        cliente.numero_documento || cliente.id || "export"
      }.${ext}`;
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      // Se muestra un toast de éxito:
      window.dispatchEvent(
        new CustomEvent("app-toast", {
          detail: { message: "Descarga completada", type: "success" },
        })
      );
      onClose();
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err.message ||
        "Error al generar exportación";
      setError(msg);
      window.dispatchEvent(
        new CustomEvent("app-toast", {
          detail: { message: msg, type: "danger" },
        })
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <style>
        {`
        .form-check-input[type="radio"] {
          border: 2px solid #000;
        }
        .form-check-input[type="radio"]:checked {
          border: 2px solid #000;
        }
      `}
      </style>
      <div className="modal d-block" tabIndex="-1" role="dialog">
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Exportar datos del cliente</h5>
              <button
                type="button"
                className="btn-close"
                aria-label="Close"
                onClick={onClose}
              ></button>
            </div>
            <div className="modal-body">
              <p>
                Seleccione el formato de exportación para{" "}
                <strong>
                  {cliente?.nombre} {cliente?.apellido}
                </strong>
                :
              </p>

              <div className="form-check">
                <input
                  className="form-check-input"
                  type="radio"
                  name="formato"
                  id="fmt-excel"
                  value="EXCEL"
                  checked={formato === "EXCEL"}
                  onChange={() => setFormato("EXCEL")}
                />
                <label className="form-check-label" htmlFor="fmt-excel">
                  EXCEL (.xlsx)
                </label>
              </div>
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="radio"
                  name="formato"
                  id="fmt-csv"
                  value="CSV"
                  checked={formato === "CSV"}
                  onChange={() => setFormato("CSV")}
                />
                <label className="form-check-label" htmlFor="fmt-csv">
                  CSV (.csv)
                </label>
              </div>
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="radio"
                  name="formato"
                  id="fmt-txt"
                  value="TXT"
                  checked={formato === "TXT"}
                  onChange={() => setFormato("TXT")}
                />
                <label className="form-check-label" htmlFor="fmt-txt">
                  TXT (.txt)
                </label>
              </div>

              {error && <div className="alert alert-danger mt-2">{error}</div>}
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                disabled={loading}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleConfirm}
                disabled={loading}
              >
                {loading ? <Loading small /> : "Confirmar y descargar"}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="modal-backdrop show"></div>
    </>
  );
}
