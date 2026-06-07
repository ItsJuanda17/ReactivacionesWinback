import { useEffect, useState } from "react";
import { api, COP, pct } from "../api.js";
import KpiCard from "../components/KpiCard.jsx";
import MetricsPanel from "../components/MetricsPanel.jsx";
import ProspectTable from "../components/ProspectTable.jsx";

export default function Dashboard() {
  const [resumen, setResumen] = useState(null);
  const [metricas, setMetricas] = useState(null);
  const [prospectos, setProspectos] = useState([]);
  const [segmento, setSegmento] = useState("");
  const [buscar, setBuscar] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    api.resumen().then(setResumen).catch(() => setError(true));
    api.metricas().then(setMetricas).catch(() => setError(true));
  }, []);

  // Recarga la tabla cuando cambian los filtros (con pequeño debounce de búsqueda)
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
          No se pudo conectar con la API. Levanta el backend en <code>{api.base}</code>.
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-head">
        <h1>Dashboard de reactivación</h1>
        <p className="subtitle">Priorización de prospectos y desempeño del modelo · estrategia Winback</p>
      </div>

      {/* KPIs */}
      <section className="section grid grid-kpi">
        {resumen ? (
          <>
            <KpiCard label="Prospectos analizados" value={resumen.total_prospectos.toLocaleString("es-CO")} />
            <KpiCard
              label="Alta probabilidad"
              value={resumen.alta_probabilidad.toLocaleString("es-CO")}
              delta={`${pct(resumen.pct_alta_probabilidad)} del total`}
              accent
            />
            <KpiCard label="Probabilidad media" value={pct(resumen.prob_media)} />
            <KpiCard label="Valor recuperable" value={COP(resumen.valor_recuperable_cop)} delta="segmentos diamante + oro" />
            <KpiCard label="Reactivados (histórico)" value={resumen.reactivados.toLocaleString("es-CO")} />
          </>
        ) : (
          <div className="loading">Cargando KPIs…</div>
        )}
      </section>

      {/* Modelo */}
      <section className="section">
        {metricas && <MetricsPanel modelos={metricas.modelos} modeloFinal={metricas.modelo_final} />}
      </section>

      {/* Ranking de prospectos */}
      <section className="section">
        <div className="card">
          <h2>Ranking de prospectos</h2>
          <p className="hint">Ordenados por probabilidad de reactivación (mayor a menor)</p>
          <div className="toolbar">
            <input
              className="input"
              placeholder="Buscar por nombre o ciudad…"
              value={buscar}
              onChange={(e) => setBuscar(e.target.value)}
            />
            <select className="select" value={segmento} onChange={(e) => setSegmento(e.target.value)}>
              <option value="">Todos los segmentos</option>
              <option value="diamante">Diamante</option>
              <option value="oro">Oro</option>
              <option value="plata">Plata</option>
              <option value="bronce">Bronce</option>
            </select>
            <span style={{ color: "var(--slate-400)", fontSize: 13 }}>{prospectos.length} resultados</span>
          </div>
          <ProspectTable prospectos={prospectos} />
        </div>
      </section>
    </div>
  );
}
