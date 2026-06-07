// Cliente HTTP minimalista para la API Winback
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function get(path) {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

export const api = {
  base: API,
  resumen: () => get("/prospectos/resumen"),
  prospectos: (params = "") => get(`/prospectos${params}`),
  metricas: () => get("/metricas"),
  arquetipos: () => get("/arquetipos"),
  shap: () => get("/modelo/importancia-variables"),
  chatbot: async (estado_actual, opcion_elegida = null) => {
    const r = await fetch(`${API}/chatbot/mensaje`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ estado_actual, opcion_elegida }),
    });
    return r.json();
  },
};

export const COP = (v) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v || 0);

export const pct = (v) => `${(v * 100).toFixed(0)}%`;
