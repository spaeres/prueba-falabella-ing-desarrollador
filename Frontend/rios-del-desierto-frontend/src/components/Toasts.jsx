import React, { useEffect, useState } from "react";

export default function Toasts() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    function handler(e) {
      const id = Date.now() + Math.random();
      const t = {
        id,
        message: e.detail.message,
        type: e.detail.type || "info",
      };
      setToasts((prev) => [...prev, t]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((x) => x.id !== id));
      }, 4000);
    }

    window.addEventListener("app-toast", handler);
    return () => window.removeEventListener("app-toast", handler);
  }, []);

  if (!toasts.length) return null;

  const iconFor = (type) => {
    switch (type) {
      case "warning":
        return "⚠️";
      case "danger":
        return "❌";
      case "success":
        return "✅";
      case "info":
      default:
        return "ℹ️";
    }
  };

  return (
    <div style={{ position: "fixed", right: 16, bottom: 16, zIndex: 1100 }}>
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`toast show align-items-center text-bg-${t.type} mb-2`}
          role="alert"
          aria-live="assertive"
          aria-atomic="true"
        >
          <div className="d-flex">
            <div
              className="toast-body"
              style={{
                fontSize: "1.05rem",
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span style={{ fontSize: "1.2rem", lineHeight: 1 }}>
                {iconFor(t.type)}
              </span>
              <div style={{ flex: 1 }}>{t.message}</div>
            </div>
            <button
              type="button"
              className="btn-close btn-close-white me-2 m-auto"
              aria-label="Close"
              onClick={() =>
                setToasts((prev) => prev.filter((x) => x.id !== t.id))
              }
            ></button>
          </div>
        </div>
      ))}
    </div>
  );
}
