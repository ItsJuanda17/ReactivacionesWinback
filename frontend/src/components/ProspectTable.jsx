import { pct } from "../api.js";

export default function ProspectTable({ prospectos }) {
  if (!prospectos.length) {
    return <div className="loading">Sin resultados.</div>;
  }
  return (
    <div className="table-wrap">
      <table className="data">
        <thead>
          <tr>
            <th>#</th>
            <th>Nombre</th>
            <th>Ciudad</th>
            <th>Plan</th>
            <th>Antigüedad</th>
            <th>Probabilidad</th>
            <th>Segmento</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {prospectos.map((p, i) => (
            <tr key={p.id}>
              <td style={{ color: "var(--slate-400)" }}>{i + 1}</td>
              <td style={{ fontWeight: 600 }}>{p.nombre_completo}</td>
              <td>{p.ciudad}</td>
              <td style={{ textTransform: "capitalize" }}>{p.plan_previo}</td>
              <td>{p.antiguedad_meses} m</td>
              <td>
                <span className="badge badge-prob">{pct(p.prob_reactivacion)}</span>
              </td>
              <td>
                <span className={`badge badge-${p.segmento}`}>{p.segmento}</span>
              </td>
              <td style={{ color: "var(--slate-500)", textTransform: "capitalize" }}>
                {p.estado_gestion?.replace("_", " ")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
