import { Link } from "react-router-dom";

const FEATURES = [
  { ic: "🎯", t: "Modelo predictivo", d: "Probabilidad de reactivación por prospecto integrando 6 fuentes de información histórica." },
  { ic: "⚖️", t: "Comparación de modelos", d: "LogReg, Random Forest y XGBoost evaluados con Accuracy, Precision, Recall, F1 y AUC." },
  { ic: "🧩", t: "Arquetipos accionables", d: "Segmentación K-Means con estrategia diferencial y recomendaciones de mercadeo." },
  { ic: "💬", t: "Chatbot de prospección", d: "Flujo winback de 5 etapas: contacto, datos, calentamiento, interés y entrega al asesor." },
  { ic: "🔍", t: "Explicabilidad del modelo", d: "Importancia de variables con SHAP y documentación metodológica completa." },
  { ic: "⚡", t: "100% operable", d: "Stack open source desplegable local o en la nube, sin costo de licencias." },
];

export default function Landing() {
  return (
    <>
      <section className="hero">
        <div className="hero-inner">
          <div>
            <span className="pill">◆ Coomeva Medicina Prepagada · Estrategia Winback</span>
            <h1 style={{ marginTop: 18 }}>
              Reactiva a tus usuarios retirados con <span className="accent">analítica e IA</span>
            </h1>
            <p className="lead">
              Identifica quién tiene mayor probabilidad de retorno, prioriza la gestión comercial
              por valor estratégico y automatiza el primer contacto. Todo en un MVP funcional.
            </p>
            <div className="cta-row">
              <Link to="/dashboard" className="btn btn-primary">Ver dashboard →</Link>
              <Link to="/chatbot" className="btn btn-ghost">Probar el chatbot</Link>
            </div>
          </div>

          <div className="hero-card">
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Ranking de prospectos</div>
            {[
              { n: "Sofía Martínez", s: "diamante", p: 86 },
              { n: "Carlos Ruiz", s: "oro", p: 72 },
              { n: "Ana Gómez", s: "oro", p: 64 },
              { n: "Jorge Daza", s: "plata", p: 48 },
            ].map((r) => (
              <div className="row" key={r.n}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{r.n}</div>
                  <span className={`badge badge-${r.s}`}>{r.s}</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div className="bar"><span style={{ width: `${r.p}%` }} /></div>
                  <strong style={{ color: "var(--green-700)", fontSize: 14 }}>{r.p}%</strong>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="features">
        <h2>Una solución para toda la estrategia de reactivación</h2>
        <p className="sub">Cubre toda la estrategia de reactivación de punta a punta.</p>
        <div className="grid grid-cards">
          {FEATURES.map((f) => (
            <div className="feature" key={f.t}>
              <div className="ic">{f.ic}</div>
              <h3>{f.t}</h3>
              <p>{f.d}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
