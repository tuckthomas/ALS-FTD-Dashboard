import { Link, useLocation } from 'react-router-dom';
import { X, Github } from 'lucide-react';
import { useEffect } from 'react';
import { createPortal } from 'react-dom';

interface NavLink {
    href: string;
    label: string;
}

interface MobileSidebarProps {
    isOpen: boolean;
    onClose: () => void;
    navLinks: NavLink[];
}

export function MobileSidebar({ isOpen, onClose, navLinks }: MobileSidebarProps) {
    const location = useLocation();

    // Close sidebar when route changes
    useEffect(() => {
        onClose();
    }, [location.pathname, onClose]);

    // Prevent body scroll when sidebar is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);

    return createPortal(
        <>
            {/* Backdrop */}
            <div
                className={`fixed inset-0 z-[200] bg-black/60 backdrop-blur-sm transition-opacity duration-300 md:hidden ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
                    }`}
                onClick={onClose}
            />

            {/* Sidebar */}
            <div
                className={`fixed top-0 left-0 z-[200] h-full w-72 bg-background border-r border-border transform transition-transform duration-300 ease-in-out md:hidden ${isOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border">
                    <div className="flex items-center gap-3">
                        <img
                            src="/f-als-ftd-dashboard-helix.png"
                            alt="ALS/FTD Logo"
                            className="h-8 w-auto"
                        />
                        <div>
                            <h2 className="text-sm font-bold text-foreground">Familial ALS & FTD</h2>
                            <p className="text-[10px] text-muted-foreground">Research Analytics</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                        aria-label="Close menu"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="p-4 space-y-2">
                    {navLinks.map((link) => {
                        const isActive = location.pathname === link.href;
                        return (
                            <Link
                                key={link.href}
                                to={link.href}
                                className={`block px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive
                                    ? 'bg-primary/10 text-primary border border-primary/20'
                                    : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
                                    }`}
                            >
                                {link.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* Footer */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
                    <a
                        href="https://github.com/tuckthomas/ALS-FTD-Dashboard.git"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-3 rounded-lg text-sm text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors"
                    >
                        <Github className="h-4 w-4" />
                        View on GitHub
                    </a>
                </div>
            </div>
        </>,
        document.body
    );
}
