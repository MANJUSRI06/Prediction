import { useState } from "react";
import { Menu, X, Leaf } from "lucide-react";
import "./navbar.css";

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  // Get the base URL for the HTML pages - adjust based on your deployment
  const AGRI_YIELD_BASE = "http://localhost:5173"; // Change this to your actual HTML pages hosting URL

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="logo">
          <Leaf className="animated-leaf" size={24} />
          <span>AgriCare</span>
        </div>

        {/* Hamburger for mobile */}
        <button
          className="menu-toggle"
          id="menuToggle"
          aria-label="Toggle navigation"
          onClick={toggleMobileMenu}
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        <ul className={`nav-links ${isMobileMenuOpen ? "show-mobile" : ""}`}>
          <li>
            <a 
              href={`${AGRI_YIELD_BASE}/agri-yield-main/home.html`} 
              target="_self"
              onClick={closeMobileMenu}
            >
              Home
            </a>
          </li>
          <li>
            <a 
              href="https://prediction-final.vercel.app/" 
              target="_self"
              onClick={closeMobileMenu}
            >
              Yield Prediction
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/diagno.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              Diagnose
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/agrilearn.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              AgriLearn
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/map.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              Fertilizer
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/weather.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              Weather
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/dasboard.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              Sales Prediction
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/government.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              Government Schema
            </a>
          </li>
          <li>
            <a
              href={`${AGRI_YIELD_BASE}/agri-yield-main/contact.html`}
              target="_self"
              onClick={closeMobileMenu}
            >
              Contact Us
            </a>
          </li>
          <li className="translate-item">
            <div id="google_translate_element"></div>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
