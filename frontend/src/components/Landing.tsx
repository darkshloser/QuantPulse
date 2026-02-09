/**
 * Landing page component for unauthenticated users.
 */

import { Link } from "react-router-dom"
import "./Landing.css"

export function Landing() {
  return (
    <div className="landing-container">
      <header className="landing-header">
        <h1>QuantPulse</h1>
        <p>Market Intelligence Platform</p>
      </header>

      <main className="landing-content">
        <section className="hero">
          <div className="hero-content">
            <h2>Advanced Market Analysis at Your Fingertips</h2>
            <p>
              QuantPulse is a powerful platform for analyzing financial markets
              and generating trading signals in real-time.
            </p>

            <div className="features">
              <div className="feature">
                <h3>Real-Time Signals</h3>
                <p>
                  Get instant market signals based on advanced technical
                  indicators
                </p>
              </div>

              <div className="feature">
                <h3>Comprehensive Analysis</h3>
                <p>
                  Track multiple symbols and analyze patterns across various
                  timeframes
                </p>
              </div>

              <div className="feature">
                <h3>Smart Notifications</h3>
                <p>
                  Receive notifications when significant market events occur on
                  your selected symbols
                </p>
              </div>

              <div className="feature">
                <h3>Symbol Management</h3>
                <p>
                  Easy access to comprehensive symbol database with real-time
                  updates
                </p>
              </div>
            </div>

            <div className="cta-buttons">
              <Link to="/login" className="btn btn-primary">
                Sign In
              </Link>
              <Link to="/register" className="btn btn-secondary">
                Create Account
              </Link>
            </div>
          </div>
        </section>

        <section className="info">
          <h3>Getting Started</h3>
          <ol>
            <li>
              <strong>Create an Account</strong> - Register with your email
              address
            </li>
            <li>
              <strong>Get Approved</strong> - An administrator will review your
              account
            </li>
            <li>
              <strong>Log In</strong> - Access the platform once approved
            </li>
            <li>
              <strong>Select Symbols</strong> - Choose the symbols you want to
              track
            </li>
            <li>
              <strong>Analyze</strong> - View real-time signals and analysis
            </li>
          </ol>
        </section>
      </main>

      <footer className="landing-footer">
        <p>&copy; 2024 QuantPulse. All rights reserved.</p>
      </footer>
    </div>
  )
}
