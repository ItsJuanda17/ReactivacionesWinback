// RF-03 — Tarjeta de arquetipo (cluster K-Means)
export default function ArchetypeCard({ arquetipo }) {
  return (
    <div style={{ border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, background: "#fff" }}>
      <h3 style={{ margin: "0 0 8px" }}>{arquetipo.nombre}</h3>
      <p style={{ margin: 0, color: "#6b7280", fontSize: 13, lineHeight: 1.6 }}>
        {arquetipo.total_prospectos} prospectos
        <br />
        Prob. media: <strong>{(arquetipo.prob_media * 100).toFixed(0)}%</strong>
        <br />
        Edad media: {arquetipo.edad_media} años
        <br />
        Antigüedad media: {arquetipo.antiguedad_media} m
        <br />
        Motivo frecuente: {arquetipo.motivo_frecuente}
        <br />
        Plan frecuente: {arquetipo.plan_frecuente}
      </p>
    </div>
  );
}
