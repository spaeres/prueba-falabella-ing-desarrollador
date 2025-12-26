import React, { useState } from "react";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";
import { descargarReporteFidelizacion } from "../utils/api";

export default function FidelizationReport() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleDownload() {
    setLoading(true);
    setError(null);
    try {
      const blob = await descargarReporteFidelizacion();
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `reporte-fidelizacion.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      window.dispatchEvent(
        new CustomEvent("app-toast", {
          detail: { message: "Reporte descargado", type: "success" },
        })
      );
    } catch (err) {
      setError(
        err?.response?.data?.message ||
          err.message ||
          "Error descargando reporte"
      );
      window.dispatchEvent(
        new CustomEvent("app-toast", {
          detail: {
            message:
              err?.response?.data?.message ||
              err.message ||
              "Error descargando reporte",
            type: "danger",
          },
        })
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <div className="card-body">
        <h5 className="card-title">Reporte de fidelización</h5>

        <p className="card-text text-justify">
          Generar un reporte en Excel con los datos básicos de cada cliente y el
          monto total de las compras del cliente en el último mes. Se descarga
          un Excel con clientes cuyo total de compras en el mes supere 5.000.000
          COP.
        </p>

        <div className="d-flex justify-content-center mt-3">
          <button
            className="btn btn-success"
            onClick={handleDownload}
            disabled={loading}
          >
            Descargar Excel
          </button>
        </div>

        {loading && <Loading />}
        <ErrorMessage message={error} />
      </div>
    </div>
  );
}
