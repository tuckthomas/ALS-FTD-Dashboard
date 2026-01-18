import React, { useEffect, useState } from 'react';
import { MainLayout } from "@/components/layout/MainLayout";
import { Card } from "@/components/ui/card";
import axios from 'axios';


function App() {
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

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
    <MainLayout>
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
            token: token,
            'with-title': 'true',
            'with-downloads': 'true',
            theme: 'transparent',
            style: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none', display: 'block' }
          })}
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-pulse text-slate-400">Loading Analytics...</div>
        </div>
      )}
    </MainLayout>
  )
}

export default App
