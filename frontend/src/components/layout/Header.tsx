import { Link, useLocation } from 'react-router-dom';
import { Github, Moon, Sun, Menu, Bell, Search } from 'lucide-react';
import { useTheme } from '../theme/ThemeProvider';
import { useState } from 'react';
import { MobileSidebar } from './MobileSidebar';

const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/trials', label: 'Trial Finder' },
];

export function Header() {
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <>
            <header className="sticky top-0 z-50 w-full border-b border-[#19c3e6]/10 bg-[#0e1315]/80 backdrop-blur-md px-4 md:px-6 py-3">
                <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-4">
                    {/* Logo and Nav */}
                    <div className="flex items-center gap-6">
                        {/* Mobile menu button */}
                        <button
                            className="md:hidden p-2 text-slate-400 hover:text-white transition-colors"
                            onClick={() => setMobileMenuOpen(true)}
                            aria-label="Open menu"
                        >
                            <Menu className="h-6 w-6" />
                        </button>

                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-3">
                            <img
                                src="/f-als-ftd-dashboard.png"
                                alt="ALS/FTD Logo"
                                className="h-10 w-auto"
                            />
                            <div className="hidden sm:block">
                                <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                                    Research Analytics
                                    <span className="bg-[#19c3e6]/10 text-[#19c3e6] text-[10px] uppercase tracking-widest px-2 py-0.5 rounded border border-[#19c3e6]/20">
                                        Beta
                                    </span>
                                </h1>
                            </div>
                        </Link>

                        {/* Desktop Nav */}
                        <nav className="hidden md:flex items-center gap-6 ml-4">
                            {navLinks.map((link) => {
                                const isActive = location.pathname === link.href ||
                                    (link.href === '/dashboard' && location.pathname === '/dashboard');
                                return (
                                    <Link
                                        key={link.href}
                                        to={link.href}
                                        className={`text-sm font-medium transition-colors ${isActive
                                            ? 'text-[#19c3e6] border-b-2 border-[#19c3e6] pb-1'
                                            : 'text-slate-400 hover:text-white'
                                            }`}
                                    >
                                        {link.label}
                                    </Link>
                                );
                            })}
                        </nav>
                    </div>

                    {/* Search and Actions */}
                    <div className="flex items-center gap-4">
                        {/* Search */}
                        <div className="relative hidden sm:block">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 h-4 w-4" />
                            <input
                                type="text"
                                placeholder="Quick Trial Search..."
                                className="bg-[#1a2629] border border-[#19c3e6]/10 rounded-lg pl-10 pr-4 py-1.5 text-xs w-48 lg:w-64 focus:ring-1 focus:ring-[#19c3e6] focus:outline-none text-white placeholder:text-slate-500"
                            />
                        </div>

                        {/* Notifications */}
                        <button className="p-2 hover:bg-[#19c3e6]/10 rounded-lg text-slate-400 hover:text-white transition-colors">
                            <Bell className="h-5 w-5" />
                        </button>

                        {/* Theme toggle */}
                        <button
                            onClick={toggleTheme}
                            className="p-2 hover:bg-[#19c3e6]/10 rounded-lg text-slate-400 hover:text-white transition-colors"
                            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
                        >
                            {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                        </button>

                        {/* GitHub */}
                        <a
                            href="https://github.com/tuckthomas/ALS-FTD-Dashboard.git"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hidden sm:block p-2 hover:bg-[#19c3e6]/10 rounded-lg text-slate-400 hover:text-white transition-colors"
                            aria-label="View Project on GitHub"
                        >
                            <Github className="h-5 w-5" />
                        </a>

                        {/* User Avatar */}
                        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-[#19c3e6] to-[#9338db] p-0.5">
                            <div className="h-full w-full rounded-full bg-[#0e1315] flex items-center justify-center text-xs font-bold text-white">
                                U
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <MobileSidebar
                isOpen={mobileMenuOpen}
                onClose={() => setMobileMenuOpen(false)}
                navLinks={navLinks}
            />
        </>
    );
}
