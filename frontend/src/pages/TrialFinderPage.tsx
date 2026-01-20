import { useState, useEffect } from 'react';
import { Download, Table } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { TrialFilters } from '../components/trials/TrialFilters';
import { TrialsTable } from '../components/trials/TrialsTable';

export function TrialFinderPage() {
    const [searchParams] = useSearchParams();
    const initialGene = searchParams.get('gene');

    const [totalCount, setTotalCount] = useState<number | null>(null);
    const [currentData, setCurrentData] = useState<any[]>([]);
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

    const exportCSV = () => {
        if (currentData.length === 0) return;

        const headers = ["NCT ID", "Title", "Sponsor", "Status", "Phase", "Study Type", "Last Updated", "Enrollment"];
        const rows = currentData.map(t => [
            t.nctId,
            `"${t.title.replace(/"/g, '""')}"`,
            `"${t.sponsor.replace(/"/g, '""')}"`,
            t.status,
            t.phase,
            t.studyType,
            t.lastUpdated,
            t.enrollment || 0
        ]);

        const csvContent = [
            headers.join(','),
            ...rows.map(r => r.join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `als_ftd_trials_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="flex flex-1 max-w-[1600px] mx-auto w-full gap-6 p-6">
            {/* Filters Sidebar - hidden on mobile */}
            <div className="hidden lg:block">
                <TrialFilters
                    onFiltersChange={setFilters}
                    initialFilters={{ genes: initialGene ? [initialGene] : [] }}
                />
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col gap-6">
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Table className="h-8 w-8 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-foreground tracking-tight">Clinical Studies</h1>
                            <p className="text-muted-foreground italic text-sm mt-1">
                                Browse <span className="text-primary font-bold not-italic">{totalCount !== null ? totalCount.toLocaleString() : '...'} active trials</span> from global registries.
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <button 
                            onClick={exportCSV}
                            disabled={currentData.length === 0}
                            className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 border border-border rounded-lg text-sm text-foreground transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Download className="h-4 w-4" />
                            Export CSV
                        </button>
                    </div>
                </div>

                {/* Table */}
                <TrialsTable filters={filters} onDataUpdate={setCurrentData} />
            </main>
        </div>
    );
}
