import React, { useState } from "react";
import "./App.css";
import SearchForm from "./components/SearchForm";
import ClientDetails from "./components/ClientDetails";
import Loading from "./components/Loading";
import ErrorMessage from "./components/ErrorMessage";
import { getClientePorDocumento, exportCliente } from "./utils/api";
import FidelizationReport from "./pages/FidelizationReport";
import Toasts from "./components/Toasts";

function App() {
  const [client, setClient] = useState(null);
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [view, setView] = useState("search");

  // Normalizar la respuesta del backend a un objeto `client` plano'
  function normalize(raw) {
    if (!raw) return null;

    const src = raw.client || raw;
    const cliente = {};

    cliente.nombre = src.nombre || src.firstName || "";
    cliente.apellido = src.apellido || src.lastName || "";

    // El documento puede venir anidado:
    if (src.documento) {
      cliente.numero_documento =
        src.documento.numeroDocumento || src.documento.numero_documento || "";
      cliente.tipo_documento =
        src.documento.tipoDocumento || src.documento.tipo_documento || "";
    } else {
      cliente.numero_documento =
        src.numeroDocumento || src.numero_documento || src.documento || "";
      cliente.tipo_documento = src.tipoDocumento || src.tipo_documento || "";
    }

    // Los otros campos:
    cliente.correo = src.correoElectronico || src.correo || src.email || "";
    cliente.telefono =
      src.telefonoCelular || src.telefono || src.telefono_celular || "";
    cliente.fecha_nacimiento =
      src.fechaNacimiento || src.fecha_nacimiento || "";
    cliente.id = src.id || src.uuid || "";
    return cliente;
  }

  async function handleSearch({ tipo, numero }) {
    setLoading(true);
    setError(null);
    setClient(null);
    setPurchases([]);
    try {
      const data = await getClientePorDocumento({ tipo, numero });

      if (data.client) {
        setClient(normalize(data.client));
        setPurchases(data.purchases || []);
      } else if (Array.isArray(data)) {
        // Si el API retorna solo un elemento en un array, tomar ese como cliente:
        setClient(normalize(data[0]) || null);
      } else {
        setClient(normalize(data) || null);
      }
    } catch (err) {
      const status = err?.response?.status;
      const serverMessage = err?.response?.data?.message || err.message;

      if (status === 404) {
        window.dispatchEvent(
          new CustomEvent("app-toast", {
            detail: {
              message: "No se encontró ningún cliente con ese número",
              type: "warning",
            },
          })
        );
        setError(null);
      } else {
        const msg = serverMessage || "Error consultando API";
        setError(msg);
        window.dispatchEvent(
          new CustomEvent("app-toast", {
            detail: { message: msg, type: "danger" },
          })
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container py-4">
      <header className="mb-4">
        <div className="mb-3">
          <h4 className="mb-0">Rios del Desierto S.A.S.</h4>
          <small className="text-muted">Buscador de clientes — SAC</small>
        </div>

        <nav className="d-flex gap-2 justify-content-center">
          <button
            onClick={() => setView("search")}
            className={
              "btn " +
              (view === "search" ? "btn-primary" : "btn-outline-primary")
            }
          >
            Busqueda de Clientes
          </button>
          <button
            onClick={() => setView("report")}
            className={
              "btn " +
              (view === "report" ? "btn-success" : "btn-outline-success")
            }
          >
            Reportes de fidelización
          </button>
        </nav>
      </header>

      {view === "search" && (
        <>
          <SearchForm onSearch={handleSearch} clientFound={!!client} />

          {loading && <Loading />}
          <ErrorMessage message={error} />

          {client && (
            <div>
              <ClientDetails client={client} />
            </div>
          )}
        </>
      )}

      {view === "report" && <FidelizationReport />}
      <Toasts />
    </div>
  );
}

export default App;
