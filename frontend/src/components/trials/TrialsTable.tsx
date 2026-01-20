import { useState, useEffect, useMemo } from 'react';
import { ColumnDef, SortingState } from '@tanstack/react-table';
import { ExternalLink } from 'lucide-react';
import axios from 'axios';
import { DataTable } from '@/components/ui/data-table';

interface Trial {
    id: string;
    nctId: string;
    title: string;
    sponsor: string;
    status: string;
    phase: string;
    studyType: string;
    lastUpdated: string;
    summary?: string;
    eligibility?: string[];
    enrollment?: number;
    url?: string;
    genes?: string[];
    interventionTypes?: string[];
}

interface TrialsTableProps {
    filters?: {
        phases?: string[];
        genes?: string[];
        status?: string;
        studyType?: string;
        interventionTypes?: string[];
        search?: string;
    };
}

const statusStyles: Record<string, string> = {
    recruiting: 'bg-emerald-500/10 text-emerald-600 dark:bg-[#2dd4bf]/20 dark:text-[#2dd4bf]',
    active: 'bg-slate-500/20 text-slate-600 dark:text-slate-400',
    completed: 'bg-blue-500/10 text-blue-600 dark:bg-[#0ea5e9]/20 dark:text-[#0ea5e9]',
    terminated: 'bg-red-500/10 text-red-600 dark:bg-red-500/20 dark:text-red-400',
    withdrawn: 'bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400',
    suspended: 'bg-orange-500/10 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400',
    pending: 'bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400',
    unknown: 'bg-slate-500/10 text-slate-500 dark:bg-slate-600/20 dark:text-slate-500',
};

const statusLabels: Record<string, string> = {
    recruiting: 'Recruiting',
    active: 'Active, Not Recruiting',
    completed: 'Completed',
    terminated: 'Terminated',
    withdrawn: 'Withdrawn',
    suspended: 'Suspended',
    pending: 'Not Yet Recruiting',
    unknown: 'Unknown',
};

const studyTypeStyles: Record<string, string> = {
    interventional: 'bg-emerald-500/10 text-emerald-600 dark:bg-[#2dd4bf]/20 dark:text-[#2dd4bf]',
    observational: 'bg-blue-500/10 text-blue-600 dark:bg-[#0ea5e9]/20 dark:text-[#0ea5e9]',
    expanded_access: 'bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400',
    unknown: 'bg-slate-500/10 text-slate-500 dark:bg-slate-600/20 dark:text-slate-500',
};

const columns: ColumnDef<Trial>[] = [
    {
        accessorKey: 'title',
        header: 'Trial Title & Identifier',
        size: 400, // Fixed width for main content
        cell: ({ row }) => (
            <div className="flex flex-col">
                <span className="text-sm font-bold text-foreground">{row.original.title}</span>
                <span className="text-[10px] font-mono text-slate-600 dark:text-slate-400 mt-1 uppercase">
                    {row.original.nctId} | {row.original.sponsor}
                </span>
            </div>
        ),
    },
    {
        accessorKey: 'status',
        header: 'Status',
        size: 160,
        cell: ({ row }) => {
            const status = row.original.status;
            const indicatorColors: Record<string, string> = {
                recruiting: 'bg-[#2dd4bf]',
                active: 'bg-slate-400',
                suspended: 'bg-orange-400',
                pending: 'bg-purple-400',
            };
            const showIndicator = ['recruiting', 'active', 'suspended', 'pending'].includes(status);
            return (
                <span className={`inline-flex items-center justify-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter whitespace-nowrap ${statusStyles[status] || statusStyles.unknown}`}>
                    {showIndicator && (
                        <span className={`h-1.5 w-1.5 rounded-full ${indicatorColors[status]} ${status === 'recruiting' ? 'animate-pulse' : ''}`} />
                    )}
                    {statusLabels[status] || status}
                </span>
            );
        },
    },
    {
        accessorKey: 'interventionTypes',
        header: 'Intervention Type',
        size: 200,
        cell: ({ row }) => {
            const types = row.original.interventionTypes || [];
            if (types.length === 0) {
                return <span className="text-[10px] bg-slate-100 text-slate-500 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700 px-2 py-0.5 rounded-full font-bold uppercase tracking-tight">N/A</span>;
            }
            // Show only the first one if multiple, or map all? Space is limited.
            // Let's show up to 2 badges.
            return (
                <div className="flex flex-wrap gap-1">
                    {types.slice(0, 2).map((type, i) => (
                        <span key={i} className="text-[10px] bg-indigo-500/10 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400 px-2 py-0.5 rounded-full font-bold uppercase tracking-tight">
                            {type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                    ))}
                    {types.length > 2 && (
                        <span className="text-[10px] text-slate-500 font-medium">+{types.length - 2}</span>
                    )}
                </div>
            );
        },
    },
    {
        accessorKey: 'phase',
        header: 'Phase',
        size: 100,
        cell: ({ row }) => (
            <span className="text-sm text-slate-700 dark:text-slate-400 font-medium">{row.original.phase}</span>
        ),
    },
    {
        accessorKey: 'studyType',
        header: 'Study Type',
        size: 150,
        cell: ({ row }) => {
            const type = row.original.studyType || 'Unknown';
            // Normalize for style lookup (e.g., "Expanded Access" -> "expanded_access")
            const styleKey = type.toLowerCase().replace(/ /g, '_');
            return (
                <span className={`text-[10px] px-2.5 py-1 rounded-full uppercase font-bold tracking-tight whitespace-nowrap ${studyTypeStyles[styleKey] || studyTypeStyles.unknown}`}>
                    {type}
                </span>
            );
        },
    },
    {
        accessorKey: 'lastUpdated',
        header: 'Last Updated',
        size: 120,
        cell: ({ row }) => (
            <span className="text-xs text-slate-600 dark:text-slate-400">{row.original.lastUpdated}</span>
        ),
    },
];

export function TrialsTable({ filters }: TrialsTableProps) {
    const [allTrials, setAllTrials] = useState<Trial[]>([]);
    const [displayedTrials, setDisplayedTrials] = useState<Trial[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [page, setPage] = useState(1);
    const pageSize = 25;
    const [sorting, setSorting] = useState<SortingState>([]);

    // Initial fetch of ALL data
    useEffect(() => {
        const fetchAllTrials = async () => {
            try {
                setIsLoading(true);
                // Fetch ONLY active trials from the new dedicated endpoint
                const response = await axios.get('/api/analytics/trial-finder-data');
                setAllTrials(response.data.trials);
            } catch (err) {
                console.error('Failed to fetch trials:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAllTrials();
    }, []);

    // Filter and Sort Logic
    const processedTrials = useMemo(() => {
        let result = [...allTrials];

        // 1. Filtering
        if (filters) {
            if (filters.search) {
                const searchLower = filters.search.toLowerCase();
                result = result.filter(t =>
                    t.title.toLowerCase().includes(searchLower) ||
                    t.nctId.toLowerCase().includes(searchLower) ||
                    t.sponsor.toLowerCase().includes(searchLower)
                );
            }

            if (filters.status) {
                // Map frontend filter values to backend normalized values if necessary, 
                // or just match against the 'status' field which is already mapped in API response.
                // The API returns simplfied status (recruiting, active, completed, etc)
                // The Filter component sends simplified status (recruiting, active, completed)
                // So direct match should work.
                result = result.filter(t => t.status === filters.status);
            }

            if (filters.studyType) {
                result = result.filter(t => t.studyType.toLowerCase() === filters.studyType?.toLowerCase());
            }

            if (filters.interventionTypes && filters.interventionTypes.length > 0) {
                // Check if trial has ANY of the selected intervention types
                result = result.filter(t => {
                    const trialTypes = (t.interventionTypes || []).map(it => it.replace(/_/g, ' ').toLowerCase());
                    const selectedTypes = filters.interventionTypes?.map(it => it.toLowerCase()) || [];

                    // Handle "Not Specified" case
                    if (selectedTypes.includes('not specified')) {
                        if (!t.interventionTypes || t.interventionTypes.length === 0) return true;
                    }

                    if (!t.interventionTypes || t.interventionTypes.length === 0) return false;

                    return trialTypes.some(it => selectedTypes.includes(it));
                });
            }

            if (filters.phases && filters.phases.length > 0) {
                // Exact match on phase string
                result = result.filter(t => filters.phases?.includes(t.phase));
            }

            if (filters.genes && filters.genes.length > 0) {
                // Check if trial has ANY of the selected genes
                // Case insensitive check
                const selectedGenes = filters.genes.map(g => g.toLowerCase());
                result = result.filter(t => {
                    if (!t.genes || t.genes.length === 0) return false;
                    return t.genes.some(g => selectedGenes.includes(g.toLowerCase()));
                });
            }
        }

        // 2. Sorting
        if (sorting.length > 0) {
            const { id, desc } = sorting[0];
            result.sort((a, b) => {
                let valA = a[id as keyof Trial];
                let valB = b[id as keyof Trial];

                // Handle undefined/null
                if (valA === undefined || valA === null) valA = '';
                if (valB === undefined || valB === null) valB = '';

                if (typeof valA === 'string') valA = valA.toLowerCase();
                if (typeof valB === 'string') valB = valB.toLowerCase();

                if (valA < valB) return desc ? 1 : -1;
                if (valA > valB) return desc ? -1 : 1;
                return 0;
            });
        } else {
            // Default sort: Last Updated desc (?) - matching backend default
            // Backend default: -status_verified_date
            // We can just rely on the order returned from backend if no sort is active, 
            // but if we filter we might lose it? Array.filter preserves order.
        }

        return result;
    }, [allTrials, filters, sorting]);

    // Pagination Logic
    useEffect(() => {
        // When filters or sorting change, reset page
        setPage(1);
    }, [filters, sorting]);

    useEffect(() => {
        const slice = processedTrials.slice(0, page * pageSize);
        setDisplayedTrials(slice);
    }, [processedTrials, page]);

    const loadMore = () => {
        if (displayedTrials.length < processedTrials.length) {
            setPage(prev => prev + 1);
        }
    };

    const hasMore = displayedTrials.length < processedTrials.length;

    const renderExpandedContent = (trial: Trial) => (
        <div className="px-6 py-4 space-y-4">
            <div className="grid grid-cols-3 gap-8">
                <div className="col-span-2 space-y-4">
                    <h4 className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 tracking-widest">
                        Study Summary
                    </h4>
                    <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                        {trial.summary || 'No summary available for this trial.'}
                    </p>
                    <div className="flex gap-4 pt-2">
                        {trial.url && (
                            <a
                                href={trial.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-bold px-4 py-2 rounded-lg transition-colors shadow-sm"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <ExternalLink className="h-3 w-3" />
                                View on ClinicalTrials.gov
                            </a>
                        )}
                    </div>
                </div>
                {trial.eligibility && trial.eligibility.length > 0 && (
                    <div className="col-span-1 space-y-4">
                        <h4 className="text-xs font-bold uppercase text-slate-500 dark:text-slate-400 tracking-widest">
                            Eligibility Criteria
                        </h4>
                        <ul className="space-y-3">
                            {trial.eligibility.slice(0, 5).map((item, i) => (
                                <li key={i} className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-slate-300 font-medium">
                                    <svg className="w-4 h-4 text-teal-600 dark:text-[#0bf3d8] shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                                        <polyline points="22,4 12,14.01 9,11.01" />
                                    </svg>
                                    {typeof item === 'string' ? item : JSON.stringify(item)}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );

    return (
        <DataTable
            columns={columns}
            data={displayedTrials}
            isLoading={isLoading}
            hasMore={hasMore}
            onLoadMore={loadMore}
            searchPlaceholder="Search trials by title, NCT ID, or sponsor..."
            expandedContent={renderExpandedContent}
            sorting={sorting}
            onSortingChange={setSorting}
        />
    );
}
