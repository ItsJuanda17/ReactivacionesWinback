import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, COPcompact, pct } from "../api.js";

const PROCESO = [
  { n: 1, t: "Identificación", d: "Detecta a los clientes retirados con riesgo y potencial de recuperación." },
  { n: 2, t: "Predicción", d: "Estima la probabilidad de retorno de cada cliente." },
  { n: 3, t: "Priorización", d: "Ordena la gestión comercial por valor esperado." },
  { n: 4, t: "Estrategia", d: "Define la oferta y el canal según el perfil del cliente." },
  { n: 5, t: "Contacto asistido", d: "Inicia la conversación de reactivación de forma guiada." },
  { n: 6, t: "Seguimiento", d: "Mide la conversión y el resultado de cada campaña." },
];

export default function Landing() {
  const [resumen, setResumen] = useState(null);

  useEffect(() => {
    api.resumen().then(setResumen).catch(() => {});
  }, []);

  const topCiudades = resumen?.por_ciudad?.slice(0, 4) || [];
  const maxOp = topCiudades.length ? topCiudades[0].oportunidades : 1;

  return (
    <>
      <section className="hero">
        <div className="hero-inner">
          <div>
            <span className="pill">Coomeva Medicina Prepagada · Estrategia de reactivación</span>
            <h1 style={{ marginTop: 18 }}>
              Recupere a los clientes con mayor probabilidad de retorno{" "}
              <span className="accent">antes que la competencia</span>
            </h1>
            <p className="lead">
              Convierta el histórico de clientes retirados en oportunidades concretas de recuperación:
              priorice la gestión comercial por valor, defina la estrategia adecuada y haga seguimiento
              a la conversión.
            </p>
            <div className="cta-row">
              <Link to="/dashboard" className="btn btn-primary">Ver tablero de gestión →</Link>
              <Link to="/asistente" className="btn btn-ghost">Probar el asistente</Link>
            </div>
          </div>

          <div className="hero-card">
            <div style={{ fontWeight: 700, marginBottom: 10, color: "var(--slate-700)" }}>
              Panorama de recuperación
            </div>
            <div className="hero-stats">
              <div>
                <div className="hs-value">{resumen ? COPcompact(resumen.valor_recuperable_cop) : "—"}</div>
                <div className="hs-label">Valor potencial recuperable</div>
              </div>
              <div>
                <div className="hs-value">{resumen ? resumen.alta_probabilidad.toLocaleString("es-CO") : "—"}</div>
                <div className="hs-label">Clientes priorizados</div>
              </div>
              <div>
                <div className="hs-value">{resumen ? pct(resumen.conversion_historica) : "—"}</div>
                <div className="hs-label">Conversión histórica</div>
              </div>
              <div>
                <div className="hs-value">{resumen ? pct(resumen.tasa_contacto_efectiva) : "—"}</div>
                <div className="hs-label">Contacto efectivo</div>
              </div>
            </div>
            {topCiudades.length > 0 && (
              <div style={{ marginTop: 14 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "var(--slate-500)", marginBottom: 8 }}>
                  Oportunidades por ciudad
                </div>
                {topCiudades.map((c) => (
                  <div className="row" key={c.ciudad}>
                    <span style={{ fontSize: 13, fontWeight: 600 }}>{c.ciudad}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div className="bar"><span style={{ width: `${(c.oportunidades / maxOp) * 100}%` }} /></div>
                      <strong style={{ color: "var(--green-700)", fontSize: 13, width: 30, textAlign: "right" }}>
                        {c.oportunidades}
                      </strong>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="features">
        <h2>Del dato histórico a la recuperación, en seis pasos</h2>
        <p className="sub">Un proceso de reactivación de extremo a extremo para el equipo comercial.</p>
        <div className="timeline">
          {PROCESO.map((p) => (
            <div className="step" key={p.n}>
              <div className="step-num">{p.n}</div>
              <h3>{p.t}</h3>
              <p>{p.d}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
