import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

export async function getClientePorDocumento({ tipo, numero }) {
  const params = { numero_documento: numero };
  if (tipo) params.tipo_documento = tipo;

  const resp = await api.get("/clientes/buscar", { params });
  return resp.data;
}

export async function exportCliente(
  tipo_documento,
  documento,
  formato = "EXCEL"
) {
  // Llama al endpoint que devuelve el archivo de exportación
  const resp = await api.get("/clientes/exportar", {
    params: {
      tipo_documento: tipo_documento,
      numero_documento: documento,
      formato,
    },
    responseType: "blob",
  });
  return resp.data;
}

export async function descargarReporteFidelizacion() {
  const resp = await api.get("/reportes/clientes-fidelizacion", {
    responseType: "blob",
  });
  return resp.data;
}

export default api;
