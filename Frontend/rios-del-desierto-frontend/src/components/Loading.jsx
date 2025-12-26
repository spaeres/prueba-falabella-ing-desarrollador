import React from "react";

export default function Loading({ small }) {
  return (
    <div className={small ? "py-1" : "py-3"}>
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>
    </div>
  );
}
