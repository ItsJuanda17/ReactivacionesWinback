const SEGMENTO_COLOR = {
  diamante: "#8B5CF6",
  oro: "#F59E0B",
  plata: "#6B7280",
  bronce: "#92400E",
};

// Tabla de ranking de prospectos ordenada por probabilidad de reactivación
export default function ProspectTable({ prospectos }) {
  const ordenados = [...prospectos].sort((a, b) => b.prob_reactivacion - a.prob_reactivacion);

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, background: "#fff" }}>
      <thead>
        <tr style={{ background: "#f9fafb", textAlign: "left" }}>
          <th style={{ padding: 8 }}>Nombre</th>
          <th style={{ padding: 8 }}>Ciudad</th>
          <th style={{ padding: 8 }}>Plan</th>
          <th style={{ padding: 8 }}>Antigüedad</th>
          <th style={{ padding: 8 }}>Probabilidad</th>
          <th style={{ padding: 8 }}>Segmento</th>
          <th style={{ padding: 8 }}>Estado</th>
        </tr>
      </thead>
      <tbody>
        {ordenados.map((p) => (
          <tr key={p.id} style={{ borderBottom: "1px solid #f3f4f6" }}>
            <td style={{ padding: 8 }}>{p.nombre_completo}</td>
            <td style={{ padding: 8 }}>{p.ciudad}</td>
            <td style={{ padding: 8 }}>{p.plan_previo}</td>
            <td style={{ padding: 8 }}>{p.antiguedad_meses} m</td>
            <td style={{ padding: 8 }}>
              <span style={{ background: "#EDE9FE", padding: "2px 8px", borderRadius: 6 }}>
                {(p.prob_reactivacion * 100).toFixed(0)}%
              </span>
            </td>
            <td style={{ padding: 8 }}>
              <span
                style={{
                  background: SEGMENTO_COLOR[p.segmento] + "22",
                  color: SEGMENTO_COLOR[p.segmento],
                  padding: "2px 8px",
                  borderRadius: 6,
                  fontWeight: 600,
                }}
              >
                {p.segmento}
              </span>
            </td>
            <td style={{ padding: 8 }}>{p.estado_gestion}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
