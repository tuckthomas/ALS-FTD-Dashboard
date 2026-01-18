export function Footer() {
    return (
        <footer className="border-t border-slate-800 bg-slate-950 py-8 text-slate-400">
            <div className="container flex flex-col items-center justify-center gap-4">
                <img
                    src="/f-als-ftd-dashboard.png"
                    alt="ALS/FTD Logo"
                    className="h-16 w-auto object-contain"
                    style={{ height: '64px' }}
                />
                <p className="text-center text-sm leading-loose">
                    &copy; 2026 ALS/FTD Research Collective.
                </p>
            </div>
        </footer>
    );
}
