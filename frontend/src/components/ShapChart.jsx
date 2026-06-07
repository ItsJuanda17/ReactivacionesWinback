import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

// RF-05 — Importancia de variables (SHAP)
export default function ShapChart({ shap, top = 10 }) {
  const data = shap.importancia_variables
    .slice(0, top)
    .map((v) => ({ label: v.label, importancia: +(v.importancia_relativa * 100).toFixed(1) }))
    .reverse();

  return (
    <div className="card">
      <h2>Importancia de variables (SHAP)</h2>
      <p className="hint">
        Aporte relativo de cada variable a la probabilidad de reactivación · modelo {shap.modelo}
      </p>
      <ResponsiveContainer width="100%" height={Math.max(300, data.length * 34)}>
        <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, left: 40, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eef2ef" horizontal={false} />
          <XAxis type="number" unit="%" tick={{ fontSize: 12 }} />
          <YAxis type="category" dataKey="label" width={130} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(v) => `${v}%`} />
          <Bar dataKey="importancia" radius={[0, 6, 6, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={i === data.length - 1 ? "#00833f" : "#5cbf86"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
