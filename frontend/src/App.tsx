import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { MainLayout } from "@/components/layout/MainLayout";
import { DashboardPage } from '@/pages/DashboardPage';
import { TrialFinderPage } from '@/pages/TrialFinderPage';
import { QueryBuilderPage } from '@/pages/QueryBuilderPage';
import { AboutPage } from '@/pages/AboutPage';


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
          <Route path="/" element={<DashboardPage />} />
          <Route path="/trials" element={<TrialFinderPage />} />
          <Route path="/query" element={<QueryBuilderPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </MainLayout>
    </ThemeProvider>
  );
}

export default App;
