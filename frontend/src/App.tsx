import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { MainLayout } from "@/components/layout/MainLayout";
import { DashboardPage } from '@/pages/DashboardPage';
import { TrialFinderPage } from '@/pages/TrialFinderPage';
import { Card } from "@/components/ui/card";
import axios from 'axios';

// Home page component - keeps the existing Metabase dashboard
function HomePage() {
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await axios.get('/api/analytics/metabase-token');
        if (response.data.token) {
          setToken(response.data.token);
        } else {
          setError("Failed to retrieve authentication token.");
        }
      } catch (err) {
        console.error("Error fetching Metabase token:", err);
        setError("Could not connect to Analytics Server.");
      }
    };

    fetchToken();
  }, []);

  return (
    <>
      {error ? (
        <div className="flex h-full items-center justify-center p-8">
          <Card className="p-6 text-red-500 border-red-200 bg-red-50">
            <h3 className="font-bold">Analytics Error</h3>
            <p>{error}</p>
          </Card>
        </div>
      ) : token ? (
        <div className="flex-1 w-full h-full bg-slate-50 relative">
          {React.createElement('metabase-dashboard', {
            token: token,
            'with-title': 'false',
            'with-downloads': 'true',
            theme: 'transparent',
            style: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none', display: 'block' }
          })}
        </div>
      ) : (
        <div className="flex h-full items-center justify-center">
          <div className="animate-pulse text-slate-400">Loading analytics...</div>
        </div>
      )}
    </>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(true);

  const handleGifLoad = () => {
    setTimeout(() => {
      setShowSplash(false);
    }, 4500);
  };

  return (
    <ThemeProvider defaultTheme="dark">
      {/* Splash Screen */}
      <div
        className={`fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black ${showSplash ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        style={{ transition: 'opacity 5s ease-in-out' }}
      >
        <img
          src="/f-als.gif"
          alt="Loading..."
          className="w-full max-w-4xl h-auto object-contain opacity-80"
          onLoad={handleGifLoad}
        />
        <div className="text-slate-400 text-2xl font-light tracking-[0.2em] mt-8 uppercase animate-pulse text-center px-4">
          Preparing your dashboard
        </div>
      </div>

      {/* Main App */}
      <MainLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/trials" element={<TrialFinderPage />} />
        </Routes>
      </MainLayout>
    </ThemeProvider>
  );
}

export default App;
