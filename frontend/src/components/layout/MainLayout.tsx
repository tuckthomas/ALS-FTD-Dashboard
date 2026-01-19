import { ReactNode } from 'react';
import { Header } from './Header';
import { Footer } from './Footer';
import { useTheme } from '../theme/ThemeProvider';

interface MainLayoutProps {
    children: ReactNode;
    showFooter?: boolean;
}

export function MainLayout({ children, showFooter = true }: MainLayoutProps) {
    const { theme } = useTheme();

    return (
        <div className={`relative flex min-h-screen flex-col ${theme === 'dark' ? 'bg-[#0e1315]' : 'bg-[#f6f8f8]'} text-slate-100`}>
            <Header />
            <main className="flex-1 flex flex-col">
                {children}
            </main>
            {showFooter && <Footer />}
        </div>
    );
}
