import { ReactNode } from 'react';
import { Header } from './Header';
import { Footer } from './Footer';

interface MainLayoutProps {
    children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
    return (
        <div className="relative flex min-h-screen flex-col bg-gray-50 text-gray-900">
            <Header />
            <main className="flex-1 flex flex-col">
                {children}
            </main>
            <Footer />
        </div>
    );
}
