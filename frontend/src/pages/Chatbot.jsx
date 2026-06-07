import { useState, useEffect, useRef } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

// RF-04 — UI estilo WhatsApp para el flujo winback simulado
export default function Chatbot() {
  const [mensajes, setMensajes] = useState([]);
  const [opciones, setOpciones] = useState([]);
  const [estado, setEstado] = useState("inicio");
  const [esFinal, setEsFinal] = useState(false);
  const fondoRef = useRef(null);

  // Carga el mensaje inicial al montar
  useEffect(() => {
    enviar("inicio", null, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    fondoRef.current?.scrollTo(0, fondoRef.current.scrollHeight);
  }, [mensajes]);

  async function enviar(estadoActual, opcion, esInicio = false) {
    if (opcion) {
      setMensajes((m) => [...m, { autor: "user", texto: opcion }]);
    }
    try {
      const r = await fetch(`${API}/chatbot/mensaje`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ estado_actual: estadoActual, opcion_elegida: opcion }),
      });
      const data = await r.json();
      setMensajes((m) => [...m, { autor: "bot", texto: data.mensaje }]);
      setOpciones(data.opciones);
      setEstado(data.estado);
      setEsFinal(data.es_final);
    } catch {
      setMensajes((m) => [...m, { autor: "bot", texto: "⚠️ No hay conexión con la API." }]);
    }
  }

  function reiniciar() {
    setMensajes([]);
    setOpciones([]);
    setEsFinal(false);
    setEstado("inicio");
    enviar("inicio", null, true);
  }

  return (
    <div style={{ padding: 24, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          width: 380,
          height: 600,
          display: "flex",
          flexDirection: "column",
          border: "1px solid #e5e7eb",
          borderRadius: 16,
          overflow: "hidden",
          background: "#ECE5DD",
        }}
      >
        <div style={{ background: "#075E54", color: "#fff", padding: "12px 16px", fontWeight: 600 }}>
          Asistente Coomeva MP
        </div>

        <div ref={fondoRef} style={{ flex: 1, overflowY: "auto", padding: 12 }}>
          {mensajes.map((m, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: m.autor === "user" ? "flex-end" : "flex-start",
                marginBottom: 8,
              }}
            >
              <div
                style={{
                  maxWidth: "75%",
                  padding: "8px 12px",
                  borderRadius: 12,
                  background: m.autor === "user" ? "#DCF8C6" : "#fff",
                  fontSize: 14,
                  boxShadow: "0 1px 1px rgba(0,0,0,0.1)",
                }}
              >
                {m.texto}
              </div>
            </div>
          ))}
        </div>

        <div style={{ padding: 12, background: "#f0f0f0", display: "flex", flexWrap: "wrap", gap: 8 }}>
          {!esFinal &&
            opciones.map((op) => (
              <button
                key={op}
                onClick={() => enviar(estado, op)}
                style={{
                  border: "1px solid #075E54",
                  color: "#075E54",
                  background: "#fff",
                  borderRadius: 20,
                  padding: "6px 14px",
                  fontSize: 13,
                  cursor: "pointer",
                }}
              >
                {op}
              </button>
            ))}
          {esFinal && (
            <button
              onClick={reiniciar}
              style={{
                border: "none",
                color: "#fff",
                background: "#075E54",
                borderRadius: 20,
                padding: "6px 14px",
                fontSize: 13,
                cursor: "pointer",
              }}
            >
              Reiniciar conversación
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
