import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const location = useLocation();

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
        </div>
      </div>
    </nav>
  );
}