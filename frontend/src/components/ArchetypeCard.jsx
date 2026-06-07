import { pct, COP } from "../api.js";

// Tarjeta de arquetipo con estrategia y recomendaciones
export default function ArchetypeCard({ arquetipo: a }) {
  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
        <h2 style={{ fontSize: 17 }}>{a.nombre}</h2>
        <span className={"chip " + (a.prioridad === "alta" ? "prio-alta" : "prio-media")}>
          {a.prioridad}
        </span>
      </div>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", fontSize: 13, color: "var(--slate-500)" }}>
        <span><strong style={{ color: "var(--ink)" }}>{a.total_prospectos}</strong> prospectos</span>
        <span>Prob. <strong style={{ color: "var(--green-700)" }}>{pct(a.prob_media)}</strong></span>
        <span>NPS {a.nps_medio}</span>
      </div>

      <div style={{ fontSize: 13, color: "var(--slate-500)" }}>
        Edad {a.edad_media} · Antigüedad {a.antiguedad_media}m · {a.motivo_frecuente} · plan {a.plan_frecuente}
        <br />
        Valor cliente medio: <strong style={{ color: "var(--ink)" }}>{COP(a.valor_cliente_medio)}</strong>
      </div>

      <div>
        <div style={{ fontSize: 12, fontWeight: 700, color: "var(--slate-700)", marginBottom: 4 }}>
          Variables que lo distinguen
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {a.variables_relevantes?.map((v, i) => (
            <span key={i} className="chip">
              {v.variable} {v.tendencia === "alta" ? "↑" : "↓"}
            </span>
          ))}
        </div>
      </div>

      <div style={{ background: "var(--green-50)", borderRadius: 10, padding: 12, fontSize: 13 }}>
        <div style={{ fontWeight: 700, color: "var(--green-700)", marginBottom: 4 }}>Estrategia</div>
        <p style={{ color: "var(--slate-700)" }}>{a.estrategia_recomendada}</p>
        <ul className="list-clean">
          <li>Canal: {a.canal_sugerido}</li>
          <li>Mercadeo: {a.recomendacion_mercadeo}</li>
        </ul>
      </div>
    </div>
  );
}
