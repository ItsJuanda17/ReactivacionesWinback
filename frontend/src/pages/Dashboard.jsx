import { useEffect, useState } from "react";
import MetricsPanel from "../components/MetricsPanel.jsx";
import ArchetypeCard from "../components/ArchetypeCard.jsx";
import ProspectTable from "../components/ProspectTable.jsx";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [prospectos, setProspectos] = useState([]);
  const [metricas, setMetricas] = useState({});
  const [arquetipos, setArquetipos] = useState([]);

  useEffect(() => {
    fetch(`${API}/prospectos?limit=50`).then((r) => r.json()).then(setProspectos).catch(() => {});
    fetch(`${API}/metricas`).then((r) => r.json()).then(setMetricas).catch(() => {});
    fetch(`${API}/arquetipos`).then((r) => r.json()).then(setArquetipos).catch(() => {});
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>Winback MVP — Coomeva MP</h1>

      {/* Métricas de modelos RF-02 */}
      {Object.keys(metricas).length > 0 && <MetricsPanel metricas={metricas} />}

      {/* Arquetipos RF-03 */}
      <section style={{ marginBottom: 32 }}>
        <h2>Arquetipos de prospectos</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 16,
          }}
        >
          {arquetipos.map((a) => (
            <ArchetypeCard key={a.id} arquetipo={a} />
          ))}
        </div>
      </section>

      {/* Tabla de prospectos con ranking */}
      <section>
        <h2>Ranking de prospectos (Top 50)</h2>
        <ProspectTable prospectos={prospectos} />
      </section>
    </div>
  );
}
