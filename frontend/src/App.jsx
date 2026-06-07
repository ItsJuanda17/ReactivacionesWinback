import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Landing from "./pages/Landing.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Arquetipos from "./pages/Arquetipos.jsx";
import Modelo from "./pages/Modelo.jsx";
import Chatbot from "./pages/Chatbot.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/arquetipos" element={<Arquetipos />} />
        <Route path="/modelo" element={<Modelo />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Route>
    </Routes>
  );
}
