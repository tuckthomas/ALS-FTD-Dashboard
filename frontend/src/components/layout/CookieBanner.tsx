import { useState, useEffect } from 'react';
import { Cookie } from 'lucide-react';
import { Button } from '../ui/button';

export function CookieBanner() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Check if user has already made a choice
        const cookies = document.cookie.split(';').reduce((acc, current) => {
            const [key, value] = current.trim().split('=');
            acc[key] = value;
            return acc;
        }, {} as Record<string, string>);

        if (!cookies['cookie_consent_status']) {
            // Small delay to not overwhelm the user immediately alongside the splash/modal
            const timer = setTimeout(() => setIsVisible(true), 1000);
            return () => clearTimeout(timer);
        }
    }, []);

    const setCookie = (status: 'accepted' | 'declined') => {
        const date = new Date();
        date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000)); // 1 year
        document.cookie = `cookie_consent_status=${status}; expires=${date.toUTCString()}; path=/; SameSite=Lax`;
        setIsVisible(false);
    };

    if (!isVisible) return null;

    return (
        <div className="fixed bottom-0 left-0 right-0 z-[200] p-4 animate-in slide-in-from-bottom duration-500">
            <div className="max-w-7xl mx-auto">
                <div className="bg-background/95 backdrop-blur-md border border-border rounded-xl shadow-2xl p-6 md:p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">

                    {/* Content */}
                    <div className="flex items-start gap-4 flex-1">
                        <div className="p-2 bg-primary/10 rounded-lg hidden md:block">
                            <Cookie className="h-6 w-6 text-primary" />
                        </div>
                        <div className="space-y-1">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                <Cookie className="h-4 w-4 text-primary md:hidden" />
                                Cookie Preferences
                            </h3>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                                We use cookies to enhance your experience and analyze platform usage.
                                By clicking "Accept", you consent to our use of cookies as described in our{' '}
                                <a href="/privacy#cookies" className="text-primary hover:underline font-medium">
                                    Cookie Policy
                                </a>.
                            </p>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto min-w-fit">
                        <Button
                            variant="outline"
                            onClick={() => setCookie('declined')}
                            className="whitespace-nowrap"
                        >
                            Decline
                        </Button>
                        <Button
                            onClick={() => setCookie('accepted')}
                            className="whitespace-nowrap bg-primary text-primary-foreground hover:bg-primary/90"
                        >
                            Accept All
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
