export default function KpiCard({ label, value, delta, accent = false }) {
  return (
    <div className={"kpi" + (accent ? " accent" : "")}>
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {delta && <div className="delta">{delta}</div>}
    </div>
  );
}
