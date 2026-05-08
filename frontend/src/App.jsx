import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import ReviewerView from './routes/ReviewerView';
import KidsView from './routes/KidsView';
import './styles/global.css';

export default function App() {
  return (
    <Router>
      <div className="app-shell">
        <nav className="main-nav">
          <Link to="/reviewer" className="nav-link">Reviewer View</Link>
          <Link to="/kids" className="nav-link">Kids View</Link>
        </nav>

        <Routes>
          <Route path="/reviewer" element={<ReviewerView />} />
          <Route path="/kids" element={<KidsView />} />
          <Route path="/" element={<Navigate to="/reviewer" replace />} />
        </Routes>
      </div>
    </Router>
  );
}
