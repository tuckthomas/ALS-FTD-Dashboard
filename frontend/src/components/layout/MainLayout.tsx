import { ReactNode } from 'react';
import { Header } from './Header';


interface MainLayoutProps {
    children: ReactNode;
    theme: 'light' | 'dark';
    onThemeToggle: () => void;
}

export function MainLayout({ children, theme, onThemeToggle }: MainLayoutProps) {
    return (
        <div className="relative flex min-h-screen flex-col bg-gray-50 text-gray-900">
            <Header theme={theme} onThemeToggle={onThemeToggle} />
            <main className="flex-1 flex flex-col">
                {children}
            </main>

        </div>
    );
}
