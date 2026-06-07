import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";

const NOMBRES = {
  logistic_regression: "Reg. Logística",
  random_forest: "Random Forest",
  xgboost: "XGBoost",
};

// Comparación de modelos
export default function MetricsPanel({ modelos, modeloFinal }) {
  const data = Object.entries(modelos).map(([k, v]) => ({
    modelo: NOMBRES[k] || k,
    key: k,
    ...v,
  }));

  return (
    <div className="card">
      <h2>Comparación de modelos</h2>
      <p className="hint">
        Modelo final: <strong>{NOMBRES[modeloFinal] || modeloFinal}</strong> (mayor F1-Score)
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eef2ef" vertical={false} />
          <XAxis dataKey="modelo" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          <Bar dataKey="f1" fill="#00833f" name="F1-Score" radius={[6, 6, 0, 0]} />
          <Bar dataKey="roc_auc" fill="#0ea5e9" name="ROC-AUC" radius={[6, 6, 0, 0]} />
          <Bar dataKey="precision" fill="#94a3b8" name="Precisión" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
