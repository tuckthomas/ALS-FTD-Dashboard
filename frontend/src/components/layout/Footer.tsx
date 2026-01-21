import { Terminal, Construction, X } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';

export function Footer() {
    const [showDevModal, setShowDevModal] = useState(false);
    const today = new Date();
    const formattedDate = new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
    }).format(today);

    const handleResourceClick = (e: React.MouseEvent) => {
        e.preventDefault();
        setShowDevModal(true);
    };

    return (
        <footer className="w-full border-t border-border bg-slate-950 dark:bg-background/80 backdrop-blur-md mt-12 relative z-40 transition-colors duration-300">
            <div className="max-w-[1600px] mx-auto px-6 py-12 mb-8">
                <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-5 gap-12 mb-12">
                    {/* Brand & Status Column */}
                    <div className="col-span-1 lg:col-span-2 flex gap-8 items-center">
                        {/* Even Larger Logo to the Left */}
                        <Link to="/" className="shrink-0">
                            <img
                                src="/f-als-ftd-dashboard-helix.png"
                                alt="ALS/FTD Logo"
                                className="h-32 w-auto"
                            />
                        </Link>

                        {/* Vertical Column for Text Content */}
                        <div className="space-y-6">                                                            <div className="flex flex-col gap-2">
                            <Link to="/" className="font-bold text-lg tracking-tight logo-gradient-text hover:opacity-80 transition-opacity">
                                ALS/FTD Research Analytics
                            </Link>
                            <p className="text-sm text-slate-400 dark:text-muted-foreground max-w-xs leading-relaxed">
                                Aggregating and visualizing clinical trial data for the familial ALS and FTD research community.
                            </p>
                        </div>
                            <div className="flex flex-col gap-1">
                                <span className="text-[10px] text-slate-500 dark:text-muted-foreground uppercase font-bold tracking-widest">
                                    Last Data Ingest
                                </span>
                                <div className="flex items-center gap-2">
                                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-xs text-slate-200 dark:text-foreground font-medium">
                                        {formattedDate}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Sitemap Columns */}
                    <div>
                        <h4 className="font-semibold text-sm text-white dark:text-foreground mb-4">Platform</h4>
                        <ul className="space-y-3 text-sm text-slate-400 dark:text-muted-foreground">
                            <li><Link to="/" className="hover:text-primary transition-colors">Dashboard</Link></li>
                            <li><Link to="/trials" className="hover:text-primary transition-colors">Trial Finder</Link></li>
                            <li><Link to="/query" className="hover:text-primary transition-colors">Query Builder</Link></li>
                            <li><Link to="/about" className="hover:text-primary transition-colors">About Project</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold text-sm text-white dark:text-foreground mb-4">Resources</h4>
                        <ul className="space-y-3 text-sm text-slate-400 dark:text-muted-foreground">
                            <li><a href="#" onClick={handleResourceClick} className="hover:text-primary transition-colors">Documentation</a></li>
                            <li><a href="/api/docs" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">API Reference</a></li>
                            <li><a href="#" onClick={handleResourceClick} className="hover:text-primary transition-colors">Research Papers</a></li>
                            <li><a href="#" onClick={handleResourceClick} className="hover:text-primary transition-colors">Data Standards</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="font-semibold text-sm text-white dark:text-foreground mb-4">Connect</h4>
                        <ul className="space-y-3 text-sm text-slate-400 dark:text-muted-foreground">
                            <li><a href="https://github.com/tuckthomas/ALS-FTD-Dashboard" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">GitHub Repository</a></li>
                            <li><Link to="/contact" className="hover:text-primary transition-colors">Contact Team</Link></li>
                            <li><Link to="/contact#report" onClick={() => window.location.hash = '#report'} className="hover:text-primary transition-colors">Report Issue</Link></li>
                            <li><div className="flex items-center gap-2 mt-2 px-3 py-1.5 rounded-md bg-slate-800 dark:bg-secondary/50 w-fit text-slate-200 dark:text-foreground">                                <Terminal className="h-3 w-3" />
                                <span className="text-[10px] font-mono">v0.1</span>
                            </div></li>
                        </ul>
                    </div>
                </div>

                <div className="flex flex-col md:flex-row justify-between items-center gap-4 pt-8 border-t border-slate-800 dark:border-border/40">
                    <p className="text-xs text-slate-500 dark:text-muted-foreground">
                        © {today.getFullYear()} ALS/FTD Research Dashboard. Open source for non-commercial research use.
                    </p>
                    <div className="flex gap-6 text-xs text-slate-400 dark:text-muted-foreground">
                        <Link to="/privacy#privacy" className="hover:text-primary transition-colors">Privacy Policy</Link>
                        <Link to="/privacy#terms" className="hover:text-primary transition-colors">Terms of Service</Link>
                        <Link to="/privacy#cookies" className="hover:text-primary transition-colors">Cookie Settings</Link>
                    </div>
                </div>

            </div>

            {/* Development Modal */}
            {showDevModal && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center px-4 bg-black/60 backdrop-blur-[2px] animate-in fade-in duration-200">
                    <div className="bg-background border border-border rounded-xl shadow-2xl max-w-sm w-full p-6 relative">
                        <button
                            onClick={() => setShowDevModal(false)}
                            className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>

                        <div className="flex flex-col items-center text-center space-y-4">
                            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                                <Construction className="h-6 w-6 text-primary" />
                            </div>

                            <div className="space-y-2">
                                <h3 className="text-lg font-semibold text-foreground">Under Construction</h3>
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                    This resource is currently in active development. Please check back later for updates.
                                </p>
                            </div>

                            <button
                                onClick={() => setShowDevModal(false)}
                                className="w-full mt-2 bg-secondary hover:bg-secondary/80 text-secondary-foreground font-medium py-2 px-4 rounded-lg transition-colors text-sm"
                            >
                                Got it
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </footer>
    );
}
