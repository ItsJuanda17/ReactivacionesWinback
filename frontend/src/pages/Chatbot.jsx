import { useState, useEffect, useRef } from "react";
import { api } from "../api.js";

// RF-04 — UI estilo WhatsApp para el flujo winback simulado
export default function Chatbot() {
  const [mensajes, setMensajes] = useState([]);
  const [opciones, setOpciones] = useState([]);
  const [estado, setEstado] = useState("inicio");
  const [esFinal, setEsFinal] = useState(false);
  const bodyRef = useRef(null);

  useEffect(() => {
    enviar("inicio", null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bodyRef.current?.scrollTo(0, bodyRef.current.scrollHeight);
  }, [mensajes]);

  async function enviar(estadoActual, opcion) {
    if (opcion) setMensajes((m) => [...m, { autor: "user", texto: opcion }]);
    try {
      const data = await api.chatbot(estadoActual, opcion);
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
    enviar("inicio", null);
  }

  return (
    <div className="page">
      <div className="page-head" style={{ textAlign: "center" }}>
        <h1>Chatbot de prospección</h1>
        <p className="subtitle">Flujo Winback: contacto → datos → calentamiento → interés → entrega al asesor (RF-04)</p>
      </div>

      <div className="chat-shell">
        <div className="chat-head">
          <div className="av">◆</div>
          <div>
            <div style={{ fontWeight: 700 }}>Asistente Coomeva MP</div>
            <div style={{ fontSize: 12, opacity: 0.8 }}>en línea</div>
          </div>
        </div>

        <div className="chat-body" ref={bodyRef}>
          {mensajes.map((m, i) => (
            <div key={i} style={{ display: "flex" }}>
              <div className={"bubble " + (m.autor === "user" ? "user" : "bot")}>{m.texto}</div>
            </div>
          ))}
        </div>

        <div className="chat-foot">
          {!esFinal &&
            opciones.map((op) => (
              <button key={op} className="opt-btn" onClick={() => enviar(estado, op)}>
                {op}
              </button>
            ))}
          {esFinal && (
            <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center" }} onClick={reiniciar}>
              Reiniciar conversación
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
