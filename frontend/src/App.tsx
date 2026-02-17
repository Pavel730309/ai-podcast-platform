import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-hot-toast';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import CreatePodcastPage from './pages/CreatePodcastPage';
import PodcastListPage from './pages/PodcastListPage';
import PodcastDetailPage from './pages/PodcastDetailPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/create" element={<CreatePodcastPage />} />
            <Route path="/podcasts" element={<PodcastListPage />} />
            <Route path="/podcast/:id" element={<PodcastDetailPage />} />
          </Routes>
        </main>
        <ToastContainer position="bottom-right" />
      </div>
    </Router>
  );
}

export default App;