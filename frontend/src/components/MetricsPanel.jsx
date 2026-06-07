import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

// RF-02 — Comparación de modelos con BarChart
export default function MetricsPanel({ metricas }) {
  const data = Object.entries(metricas).map(([k, v]) => ({ modelo: k, ...v }));

  return (
    <section style={{ marginBottom: 32 }}>
      <h2>Comparación de modelos</h2>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <XAxis dataKey="modelo" />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Legend />
          <Bar dataKey="f1" fill="#8B5CF6" name="F1-Score" />
          <Bar dataKey="roc_auc" fill="#06B6D4" name="ROC-AUC" />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}
