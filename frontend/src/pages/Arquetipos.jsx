import { useEffect, useState } from "react";
import { api } from "../api.js";
import ArchetypeCard from "../components/ArchetypeCard.jsx";

export default function Arquetipos() {
  const [arquetipos, setArquetipos] = useState([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    api.arquetipos().then(setArquetipos).catch(() => setError(true));
  }, []);

  return (
    <div className="page">
      <div className="page-head">
        <h1>Arquetipos accionables</h1>
        <p className="subtitle">
          Segmentación K-Means con estrategia diferencial de contacto y recomendaciones de mercadeo (RF-03)
        </p>
      </div>

      {error && <div className="card loading">No se pudo conectar con la API.</div>}

      <section className="grid grid-cards">
        {arquetipos.map((a) => (
          <ArchetypeCard key={a.id} arquetipo={a} />
        ))}
      </section>
    </div>
  );
}
