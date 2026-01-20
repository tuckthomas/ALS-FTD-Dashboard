import { Link, useLocation } from 'react-router-dom';
import { Github, Moon, Sun, Menu, Bell } from 'lucide-react';
import { useTheme } from '../theme/ThemeProvider';
import { useState, useCallback } from 'react';
import { MobileSidebar } from './MobileSidebar';

const navLinks = [
    { href: '/', label: 'Dashboard' },
    { href: '/about', label: 'About' },
    { href: '/trials', label: 'Trial Finder' },
    { href: '/news', label: 'News' },
    { href: '/query', label: 'Query Builder' },
];

export function Header() {
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const closeMobileMenu = useCallback(() => setMobileMenuOpen(false), []);

    return (
        <>
            <header className="sticky top-0 z-50 w-full border-b border-border bg-slate-950 dark:bg-background/80 backdrop-blur-md px-4 md:px-6 py-3 transition-colors duration-300">
                <div className="max-w-[1600px] mx-auto flex items-center justify-between gap-4">
                    {/* Logo and Nav */}
                    <div className="flex items-center gap-6">
                        {/* Mobile menu button */}
                        <button
                            className="md:hidden p-2 text-slate-400 hover:text-white dark:text-muted-foreground dark:hover:text-foreground transition-colors"
                            onClick={() => {
                                console.log('Mobile menu button clicked');
                                setMobileMenuOpen(true);
                            }}
                            aria-label="Open menu"
                        >
                            <Menu className="h-6 w-6" />
                        </button>

                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-3">
                            <img
                                src="/f-als-ftd-dashboard-helix.png"
                                alt="ALS/FTD Logo"
                                className="h-10 w-auto"
                            />
                            <div className="hidden sm:block">
                                <h1 className="text-lg font-bold tracking-tight logo-gradient-text flex items-center gap-2">
                                    Familial ALS & FTD Research Analytics
                                    <span className="bg-primary/10 text-primary text-[10px] uppercase tracking-widest px-2 py-0.5 rounded border border-primary/20">
                                        Beta
                                    </span>
                                </h1>
                            </div>
                        </Link>

                        {/* Desktop Nav */}
                        <nav className="hidden md:flex items-center gap-6 ml-4">
                            {navLinks.map((link) => {
                                const isActive = location.pathname === link.href ||
                                    (link.href === '/' && location.pathname === '/');
                                return (
                                    <Link
                                        key={link.href}
                                        to={link.href}
                                        className={`text-sm font-medium transition-colors ${isActive
                                            ? 'text-primary border-b-2 border-primary pb-1'
                                            : 'text-slate-400 hover:text-white dark:text-muted-foreground dark:hover:text-foreground'
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


                        {/* Notifications */}
                        <button className="p-2 hover:bg-slate-800 hover:text-white dark:hover:bg-accent dark:hover:text-accent-foreground rounded-lg text-slate-400 dark:text-muted-foreground transition-colors">
                            <Bell className="h-5 w-5" />
                        </button>

                        {/* Theme toggle */}
                        <button
                            onClick={toggleTheme}
                            className="p-2 hover:bg-slate-800 hover:text-white dark:hover:bg-accent dark:hover:text-accent-foreground rounded-lg text-slate-400 dark:text-muted-foreground transition-colors"
                            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
                        >
                            {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
                        </button>

                        {/* GitHub */}
                        <a
                            href="https://github.com/tuckthomas/ALS-FTD-Dashboard.git"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hidden sm:block p-2 hover:bg-slate-800 hover:text-white dark:hover:bg-accent dark:hover:text-accent-foreground rounded-lg text-slate-400 dark:text-muted-foreground transition-colors"
                            aria-label="View Project on GitHub"
                        >
                            <Github className="h-5 w-5" />
                        </a>

                        {/* User Avatar */}
                        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-[#19c3e6] to-[#9338db] p-0.5">
                            <div className="h-full w-full rounded-full bg-slate-950 dark:bg-background flex items-center justify-center text-xs font-bold text-white dark:text-foreground">
                                U
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <MobileSidebar
                isOpen={mobileMenuOpen}
                onClose={closeMobileMenu}
                navLinks={navLinks}
            />
        </>
    );
}
