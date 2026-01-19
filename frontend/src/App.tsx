import React, { useEffect, useState } from 'react';
import { MainLayout } from "@/components/layout/MainLayout";
import { Card } from "@/components/ui/card";
import axios from 'axios';


function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    if (window.metabaseConfig && window.metabaseConfig.theme) {
      window.metabaseConfig.theme.preset = newTheme;
    }
  };

  const handleGifLoad = () => {
    // Only start the timer once the GIF has actually loaded
    setTimeout(() => {
      setShowSplash(false);
    }, 4500); // Increased display time
  };

  useEffect(() => {
    const fetchToken = async () => {
      try {
        // Fetch from our local API (which generates the JWT)
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

      <MainLayout theme={theme} onThemeToggle={toggleTheme}>
        {error ? (
          <div className="flex h-full items-center justify-center p-8">
            <Card className="p-6 text-red-500 border-red-200 bg-red-50">
              <h3 className="font-bold">Analytics Error</h3>
              <p>{error}</p>
            </Card>
          </div>
        ) : token ? (
          <div className="flex-1 w-full h-full bg-slate-50 relative">
            {/* 
                Metabase Web Component 
                Using createElement to bypass TypeScript IntrinsicElements check
             */}
            {React.createElement('metabase-dashboard', {
              key: theme,
              token: token,
              'with-title': 'false',
              'with-downloads': 'true',
              theme: 'transparent',
              style: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none', display: 'block' }
            })}
          </div>
        ) : null}
      </MainLayout>
    </>
  )
}

export default App
