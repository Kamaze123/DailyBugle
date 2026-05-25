import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { runPipeline } from "../api";
import "./Navbar.css";

export default function Navbar() {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleRefresh = async () => {
    setLoading(true);
    setStatus(null);
    try {
      const res = await runPipeline();
      setStatus(`✓ ${res.articles_processed} articles loaded`);
    } catch {
      setStatus("Failed to fetch news");
    } finally {
      setLoading(false);
      setTimeout(() => setStatus(null), 4000);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-left">
          <span className="navbar-date">
            {new Date().toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </span>
        </div>

        <Link to="/" className="navbar-masthead">
          Daily Bugle
        </Link>

        <div className="navbar-right">
          <Link to="/" className={`nav-link ${location.pathname === "/" ? "active" : ""}`}>
            Digest
          </Link>
          <Link to="/chat" className={`nav-link ${location.pathname === "/chat" ? "active" : ""}`}>
            Ask
          </Link>
          <button
            className={`refresh-btn ${loading ? "loading" : ""}`}
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? "Fetching..." : "Refresh"}
          </button>
          {status && <span className="status-msg">{status}</span>}
        </div>
      </div>
    </nav>
  );
}