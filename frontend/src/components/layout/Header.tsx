import { Github, Moon, Sun } from 'lucide-react';

interface HeaderProps {
    theme: 'light' | 'dark';
    onThemeToggle: () => void;
}

export function Header({ theme, onThemeToggle }: HeaderProps) {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950 shadow-md">
            <div className="flex h-16 items-center px-10 w-full justify-between">
                <div className="flex items-center gap-3">
                    <img
                        src="/f-als-ftd-dashboard.png"
                        alt="ALS/FTD Logo"
                        className="h-10 w-auto"
                    />
                    <span className="text-xl font-bold tracking-tight text-slate-400">Familial ALS & FTD Dashboard</span>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={onThemeToggle}
                        className="text-slate-400 hover:text-white transition-colors p-2"
                        aria-label={theme === 'light' ? "Switch to dark mode" : "Switch to light mode"}
                    >
                        {theme === 'light' ? <Moon className="h-6 w-6" /> : <Sun className="h-6 w-6" />}
                    </button>
                    <a
                        href="https://github.com/tuckthomas/ALS-FTD-Dashboard.git"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-400 hover:text-white transition-colors p-2"
                        aria-label="View Project on GitHub"
                    >
                        <Github className="h-6 w-6" />
                    </a>
                </div>
            </div>
        </header>
    );
}
