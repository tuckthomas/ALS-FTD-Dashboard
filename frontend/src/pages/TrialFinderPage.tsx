import { Download } from 'lucide-react';
import { TrialFilters } from '../components/trials/TrialFilters';
import { TrialsTable } from '../components/trials/TrialsTable';

export function TrialFinderPage() {
    return (
        <div className="flex flex-1 max-w-[1600px] mx-auto w-full gap-6 p-6 overflow-hidden">
            {/* Filters Sidebar - hidden on mobile */}
            <div className="hidden lg:block">
                <TrialFilters />
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col gap-6 overflow-hidden">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Clinical Studies</h1>
                        <p className="text-slate-400 text-sm mt-1">
                            Found <span className="text-[#2dd4bf] font-bold">42 active trials</span> matching your criteria
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="flex items-center gap-2 px-4 py-2 bg-[#1e293b] hover:bg-[#334155] border border-[#334155] rounded-lg text-sm text-white transition-all">
                            <Download className="h-4 w-4" />
                            Export CSV
                        </button>
                    </div>
                </div>

                {/* Table */}
                <TrialsTable />
            </main>
        </div>
    );
}
