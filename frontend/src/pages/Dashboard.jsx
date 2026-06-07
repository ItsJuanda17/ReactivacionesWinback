import { useEffect, useState } from "react";
import { api, COP, pct, PRIORIDAD } from "../api.js";
import ProspectTable from "../components/ProspectTable.jsx";
import Insights from "../components/Insights.jsx";

export default function Dashboard() {
  const [resumen, setResumen] = useState(null);
  const [hallazgos, setHallazgos] = useState([]);
  const [prospectos, setProspectos] = useState([]);
  const [segmento, setSegmento] = useState("");
  const [buscar, setBuscar] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    api.resumen().then(setResumen).catch(() => setError(true));
    api.insights().then((d) => setHallazgos(d.hallazgos)).catch(() => {});
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      const qs = new URLSearchParams({ limit: "100" });
      if (segmento) qs.set("segmento", segmento);
      if (buscar) qs.set("buscar", buscar);
      api.prospectos(`?${qs}`).then(setProspectos).catch(() => setProspectos([]));
    }, 250);
    return () => clearTimeout(t);
  }, [segmento, buscar]);

  if (error) {
    return (
      <div className="page">
        <div className="card loading">
          No se pudo conectar con el servidor. Inicia el backend en <code>{api.base}</code>.
        </div>
      </div>
    );
  }

  const ciudades = resumen?.por_ciudad || [];
  const maxOp = ciudades.length ? ciudades[0].oportunidades : 1;
  const prioridades = resumen
    ? Object.keys(PRIORIDAD).map((seg) => ({
        ...PRIORIDAD[seg],
        total: resumen.por_segmento[seg] || 0,
      }))
    : [];
  const maxPrio = Math.max(1, ...prioridades.map((p) => p.total));

  return (
    <div className="page">
      <div className="page-head">
        <h1>Tablero de gestión comercial</h1>
        <p className="subtitle">Oportunidades de reactivación priorizadas por valor de negocio</p>
      </div>

      {/* Jerarquía: KPI principal destacado + métricas secundarias */}
      <section className="section dash-hero">
        <div className="kpi-feature">
          <div className="label">Valor potencial recuperable</div>
          <div className="value">{resumen ? COP(resumen.valor_recuperable_cop) : "—"}</div>
          <div className="ctx">
            Suma del valor de plan de los {resumen?.alta_probabilidad?.toLocaleString("es-CO") || "—"}{" "}
            clientes con alta probabilidad de retorno.
          </div>
        </div>

        <div className="kpi-secondary">
          <div className="kpi">
            <div className="label">Clientes priorizados</div>
            <div className="value">{resumen ? resumen.alta_probabilidad.toLocaleString("es-CO") : "—"}</div>
            <div className="ctx">{resumen ? `${pct(resumen.pct_alta_probabilidad)} del universo analizado` : ""}</div>
          </div>
          <div className="kpi">
            <div className="label">Conversión histórica</div>
            <div className="value">{resumen ? pct(resumen.conversion_historica) : "—"}</div>
            <div className="ctx">De cliente contactado a reactivado</div>
          </div>
          <div className="kpi">
            <div className="label">Contacto efectivo</div>
            <div className="value">{resumen ? pct(resumen.tasa_contacto_efectiva) : "—"}</div>
            <div className="ctx">Gestiones que generan interés o reactivación</div>
          </div>
          <div className="kpi">
            <div className="label">Reactivados</div>
            <div className="value">{resumen ? resumen.reactivados.toLocaleString("es-CO") : "—"}</div>
            <div className="ctx">Recuperados en los últimos 12 meses</div>
          </div>
        </div>
      </section>

      {/* Distribución: ciudades (principal) + prioridad */}
      <section className="section grid-2-asym">
        <div className="card">
          <h2>Oportunidades por ciudad</h2>
          <p className="hint">Clientes priorizables según su sede</p>
          <div className="barlist">
            {ciudades.map((c) => (
              <div className="barlist-row" key={c.ciudad}>
                <span className="barlist-label">{c.ciudad}</span>
                <div className="barlist-track">
                  <span style={{ width: `${(c.oportunidades / maxOp) * 100}%` }} />
                </div>
                <span className="barlist-val">{c.oportunidades}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>Distribución por prioridad</h2>
          <p className="hint">Universo de clientes retirados</p>
          <div className="barlist">
            {prioridades.map((p) => (
              <div className="barlist-row" key={p.label}>
                <span className="barlist-label" style={{ width: 120 }}>{p.label}</span>
                <div className="barlist-track">
                  <span className={`fill-${p.cls}`} style={{ width: `${(p.total / maxPrio) * 100}%` }} />
                </div>
                <span className="barlist-val">{p.total}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Hallazgos */}
      <section className="section">
        <Insights hallazgos={hallazgos} />
      </section>

      {/* Ranking */}
      <section className="section">
        <div className="card">
          <h2>Clientes priorizados para gestión</h2>
          <p className="hint">Ordenados por probabilidad de retorno</p>
          <div className="toolbar">
            <input
              className="input"
              placeholder="Buscar por nombre o ciudad…"
              value={buscar}
              onChange={(e) => setBuscar(e.target.value)}
            />
            <select className="select" value={segmento} onChange={(e) => setSegmento(e.target.value)}>
              <option value="">Todas las prioridades</option>
              <option value="diamante">Alta prioridad</option>
              <option value="oro">Prioridad media</option>
              <option value="plata">Seguimiento</option>
              <option value="bronce">Baja prioridad</option>
            </select>
            <span style={{ color: "var(--slate-400)", fontSize: 13 }}>{prospectos.length} clientes</span>
          </div>
          <ProspectTable prospectos={prospectos} />
        </div>
      </section>
    </div>
  );
}
