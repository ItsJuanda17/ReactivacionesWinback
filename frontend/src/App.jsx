import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Chatbot from "./pages/Chatbot.jsx";

const navStyle = ({ isActive }) => ({
  padding: "8px 16px",
  borderRadius: 8,
  textDecoration: "none",
  color: isActive ? "#fff" : "#4b5563",
  background: isActive ? "#8B5CF6" : "transparent",
  fontWeight: 600,
});

export default function App() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", minHeight: "100vh", background: "#f8fafc" }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          padding: "12px 24px",
          background: "#fff",
          borderBottom: "1px solid #e5e7eb",
        }}
      >
        <strong style={{ fontSize: 18, color: "#111827" }}>Winback · Coomeva MP</strong>
        <nav style={{ display: "flex", gap: 8 }}>
          <NavLink to="/" style={navStyle} end>
            Dashboard
          </NavLink>
          <NavLink to="/chatbot" style={navStyle}>
            Chatbot
          </NavLink>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Routes>
    </div>
  );
}
