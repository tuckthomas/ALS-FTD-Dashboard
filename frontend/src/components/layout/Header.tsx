export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950 shadow-md">
            <div className="flex h-16 items-center px-10 w-full">
                <div className="flex items-center gap-3">
                    <img
                        src="/f-als-ftd-dashboard.png"
                        alt="ALS/FTD Logo"
                        className="h-10 w-auto"
                    />
                    <span className="text-xl font-bold tracking-tight text-slate-400">Familial ALS & FTD Dashboard</span>
                </div>
            </div>
        </header>
    );
}
