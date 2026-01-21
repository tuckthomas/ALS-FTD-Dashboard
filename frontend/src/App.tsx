import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { MainLayout } from "@/components/layout/MainLayout";
import { DashboardPage } from '@/pages/DashboardPage';
import { TrialFinderPage } from '@/pages/TrialFinderPage';
import { QueryBuilderPage } from '@/pages/QueryBuilderPage';
import { AboutPage } from '@/pages/AboutPage';
import { PrivacyPage } from '@/pages/PrivacyPage';
import { ContactPage } from '@/pages/ContactPage';
import { NewsPage } from '@/pages/NewsPage';
import { GenesPage } from '@/pages/GenesPage';
import { GenePage } from '@/pages/GenePage';
import { CookieBanner } from '@/components/layout/CookieBanner';


function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [showDisclaimer, setShowDisclaimer] = useState(false);

  useEffect(() => {
    // Splash Screen Timer
    const timer = setTimeout(() => {
      setShowSplash(false);

      // Check for disclaimer cookie
      const cookies = document.cookie.split(';').reduce((acc, current) => {
        const [key, value] = current.trim().split('=');
        acc[key] = value;
        return acc;
      }, {} as Record<string, string>);

      if (cookies['disclaimerAccepted'] !== 'true') {
        setTimeout(() => setShowDisclaimer(true), 1000);
      }
    }, 4500);

    return () => clearTimeout(timer);
  }, []);

  const handleAcceptDisclaimer = () => {
    // Set cookie for 30 days
    const date = new Date();
    date.setTime(date.getTime() + (30 * 24 * 60 * 60 * 1000));
    document.cookie = `disclaimerAccepted=true; expires=${date.toUTCString()}; path=/; SameSite=Lax`;

    setShowDisclaimer(false);
  };

  return (
    <ThemeProvider defaultTheme="dark">
      {/* Splash Screen */}
      <div
        className={`fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black ${showSplash ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        style={{ transition: 'opacity 2.5s ease-in-out' }}
      >
        <img
          src="/f-als.gif"
          alt="Loading..."
          className="w-full max-w-4xl h-auto object-contain opacity-80"
        />
        <div className="text-slate-400 text-2xl font-light tracking-[0.2em] mt-8 uppercase animate-pulse text-center px-4">
          Preparing your dashboard
        </div>
      </div>

      {/* Disclaimer Modal */}
      {showDisclaimer && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center px-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-500">
          <div className="bg-background border border-border rounded-xl shadow-2xl max-w-lg w-full p-8 relative overflow-hidden">
            {/* Decor/Accent */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#19c3e6] to-transparent opacity-50" />

            <div className="space-y-6">
              <div className="space-y-2 text-center">
                <h2 className="text-xl font-bold tracking-tight text-foreground uppercase">Work in Progress</h2>
                <p className="text-sm text-muted-foreground">
                  This platform is currently in active development (Beta v0.1)
                </p>
              </div>

              <div className="bg-secondary/30 rounded-lg p-4 border border-border/50">
                <p className="text-sm text-muted-foreground leading-relaxed text-center">
                  <span className="font-bold text-foreground">Disclaimer:</span> This dashboard is for informational and research purposes only. It does not constitute medical advice. Always consult with a qualified healthcare provider regarding medical conditions or clinical trial participation.
                </p>
              </div>

              <div className="text-center space-y-2">
                <p className="text-xs text-muted-foreground">
                  Have questions, feedback, or suggestions?
                </p>
                <a href="mailto:tuckerolson13@gmail.com" className="text-sm font-medium text-primary hover:underline hover:text-primary/80 transition-colors">
                  tuckerolson13@gmail.com
                </a>
              </div>

              <button
                onClick={handleAcceptDisclaimer}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-bold py-3 px-4 rounded-lg transition-all transform active:scale-[0.98]"
              >
                I Understand & Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main App */}
      <MainLayout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/trials" element={<TrialFinderPage />} />
          <Route path="/query" element={<QueryBuilderPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/genes" element={<GenesPage />} />
          <Route path="/gene/:symbol" element={<GenePage />} />
        </Routes>
      </MainLayout>
      <CookieBanner />
    </ThemeProvider>
  );
}

export default App;
