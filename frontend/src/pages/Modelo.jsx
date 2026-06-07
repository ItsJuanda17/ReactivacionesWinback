import { useEffect, useState } from "react";
import { api } from "../api.js";
import MetricsPanel from "../components/MetricsPanel.jsx";
import ShapChart from "../components/ShapChart.jsx";

const NOMBRES = { logistic_regression: "Reg. Logística", random_forest: "Random Forest", xgboost: "XGBoost" };
const METRICAS = ["accuracy", "precision", "recall", "f1", "roc_auc"];
const M_LABEL = { accuracy: "Accuracy", precision: "Precision", recall: "Recall", f1: "F1-Score", roc_auc: "ROC-AUC" };

export default function Modelo() {
  const [metricas, setMetricas] = useState(null);
  const [shap, setShap] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    api.metricas().then(setMetricas).catch(() => setError(true));
    api.shap().then(setShap).catch(() => setError(true));
  }, []);

  if (error) return <div className="page"><div className="card loading">No se pudo conectar con la API.</div></div>;
  if (!metricas) return <div className="page"><div className="loading">Cargando…</div></div>;

  return (
    <div className="page">
      <div className="page-head">
        <h1>Cómo funciona la solución</h1>
        <p className="subtitle">
          Ficha metodológica: cómo se priorizan los clientes, qué información se usa y cómo se valida.
        </p>
      </div>

      {/* Ficha técnica */}
      <section className="section grid grid-kpi">
        <div className="kpi accent">
          <div className="label">Modelo final</div>
          <div className="value" style={{ fontSize: 22 }}>{NOMBRES[metricas.modelo_final]}</div>
          <div className="delta">{metricas.criterio_seleccion}</div>
        </div>
        <div className="kpi">
          <div className="label">Punto de corte</div>
          <div className="value">{metricas.punto_de_corte}</div>
          <div className="delta">prob. ≥ corte ⇒ alta intención</div>
        </div>
        <div className="kpi">
          <div className="label">Variables de entrada</div>
          <div className="value">{metricas.n_variables}</div>
          <div className="delta">de 6 fuentes consolidadas</div>
        </div>
        <div className="kpi">
          <div className="label">Balanceo de clases</div>
          <div className="value" style={{ fontSize: 20 }}>SMOTE</div>
          <div className="delta">solo en entrenamiento</div>
        </div>
      </section>

      {/* Comparación */}
      <section className="section">
        <MetricsPanel modelos={metricas.modelos} modeloFinal={metricas.modelo_final} />
      </section>

      {/* Tabla de métricas completa */}
      <section className="section">
        <div className="card">
          <h2>Métricas de desempeño</h2>
          <p className="hint">Evaluación sobre el conjunto de prueba ({metricas.n_test} registros)</p>
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>Modelo</th>
                  {METRICAS.map((m) => <th key={m}>{M_LABEL[m]}</th>)}
                </tr>
              </thead>
              <tbody>
                {Object.entries(metricas.modelos).map(([k, v]) => (
                  <tr key={k} style={k === metricas.modelo_final ? { background: "var(--green-50)" } : {}}>
                    <td style={{ fontWeight: 600 }}>
                      {NOMBRES[k]} {k === metricas.modelo_final && <span className="chip">final</span>}
                    </td>
                    {METRICAS.map((m) => <td key={m}>{v[m]}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* SHAP */}
      <section className="section">{shap && <ShapChart shap={shap} />}</section>

      {/* Hiperparámetros */}
      <section className="section">
        <div className="card">
          <h2>Hiperparámetros</h2>
          <p className="hint">Configuración de cada modelo entrenado</p>
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Modelo</th><th>Hiperparámetros</th></tr></thead>
              <tbody>
                {Object.entries(metricas.hiperparametros || {}).map(([k, v]) => (
                  <tr key={k}>
                    <td style={{ fontWeight: 600 }}>{NOMBRES[k]}</td>
                    <td style={{ fontFamily: "monospace", fontSize: 13 }}>
                      {Object.entries(v).map(([hk, hv]) => `${hk}=${hv}`).join(" · ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}
