import { NavLink, Outlet } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Inicio", end: true },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/arquetipos", label: "Arquetipos" },
  { to: "/modelo", label: "Modelo" },
  { to: "/chatbot", label: "Chatbot" },
];

export default function Layout() {
  return (
    <>
      <header className="navbar">
        <NavLink to="/" className="brand">
          <span className="brand-dot">◆</span>
          Winback · Coomeva MP
        </NavLink>
        <nav style={{ display: "flex", gap: 4 }}>
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="footer">
        Winback · Coomeva Medicina Prepagada · Estrategia de reactivación
      </footer>
    </>
  );
}
