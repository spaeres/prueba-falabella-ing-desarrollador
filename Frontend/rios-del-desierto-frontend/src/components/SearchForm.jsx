import React, { useState } from "react";

export default function SearchForm({ onSearch, clientFound = false }) {
  const [tipo, setTipo] = useState("CEDULA");
  const [numero, setNumero] = useState("");
  const [showError, setShowError] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();

    if (!numero.trim()) {
      setShowError(true);
      return;
    }

    setShowError(false);
    onSearch({ tipo, numero });
  }

  return (
    <form onSubmit={handleSubmit} className={`row g-2 align-items-end ${clientFound ? 'justify-content-center' : ''}`}>
      <div className="col-auto">
        <label className="form-label">Tipo</label>
        <select
          className="form-select"
          value={tipo}
          onChange={(e) => setTipo(e.target.value)}
        >
          <option value="NIT">NIT</option>
          <option value="CEDULA">Cédula</option>
          <option value="PASAPORTE">Pasaporte</option>
        </select>
      </div>

      <div className="col-auto position-relative">
        <label className="form-label">Número</label>
        <input
          className={`form-control ${showError ? "is-invalid" : ""}`}
          value={numero}
          onChange={(e) => {
            setNumero(e.target.value);
            if (e.target.value) setShowError(false);
          }}
          placeholder="Ingrese número"
        />

        {showError && (
          <div className="invalid-tooltip d-block">
            Agrega el número de documento
          </div>
        )}
      </div>

      <div className="col-auto">
        <button type="submit" className="btn btn-primary">
          Buscar
        </button>
      </div>
    </form>
  );
}
