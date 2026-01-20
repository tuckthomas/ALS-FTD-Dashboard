import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { TrialFilters } from '../components/trials/TrialFilters';
import { TrialsTable } from '../components/trials/TrialsTable';

export function TrialFinderPage() {
    const [searchParams] = useSearchParams();
    const initialGene = searchParams.get('gene');

    const [totalCount, setTotalCount] = useState<number | null>(null);
    const [filters, setFilters] = useState({
        phases: [] as string[],
        genes: initialGene ? [initialGene] : [] as string[],
        status: '',
        studyType: '',
        interventionTypes: [] as string[],
        search: '',
    });

    // Fetch initial count
    useEffect(() => {
        axios.get('/api/analytics/summary').then(res => {
            setTotalCount(res.data.active_trials);
        }).catch(() => { });
    }, []);

    return (
        <div className="flex flex-1 max-w-[1600px] mx-auto w-full gap-6 p-6 overflow-hidden">
            {/* Filters Sidebar - hidden on mobile */}
            <div className="hidden lg:block">
                <TrialFilters
                    onFiltersChange={setFilters}
                    initialFilters={{ genes: initialGene ? [initialGene] : [] }}
                />
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col gap-6 overflow-hidden">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
                    <div>
                        <h1 className="text-3xl font-bold text-foreground tracking-tight">Clinical Studies</h1>
                        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">
                            Browse <span className="text-primary font-bold">{totalCount !== null ? totalCount.toLocaleString() : '...'} active trials</span> from global registries
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 border border-border rounded-lg text-sm text-foreground transition-all">
                            <Download className="h-4 w-4" />
                            Export CSV
                        </button>
                    </div>
                </div>

                {/* Table */}
                <TrialsTable filters={filters} />
            </main>
        </div>
    );
}
