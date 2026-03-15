import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Landing from './pages/Landing';
import Auth from './pages/Auth';
import UploadDashboard from './pages/UploadDashboard';

function App() {
  return (
    <Router>
      <div className="bg-dark min-h-screen text-white font-sans">
        <Navbar />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/dashboard" element={<UploadDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
