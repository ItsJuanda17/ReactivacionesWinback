// Hallazgos de negocio derivados del análisis de la base
export default function Insights({ hallazgos }) {
  if (!hallazgos?.length) return null;
  return (
    <div className="card">
      <h2>Hallazgos del análisis</h2>
      <p className="hint">Patrones detectados en la base de clientes retirados</p>
      <div className="insight-list">
        {hallazgos.map((h, i) => (
          <div className="insight" key={i}>
            <div className="insight-mark" />
            <div>
              <div className="insight-title">{h.titulo}</div>
              <p className="insight-detail">{h.detalle}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
