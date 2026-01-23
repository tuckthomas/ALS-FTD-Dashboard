import { useState, useEffect, useMemo } from 'react';
import { ColumnDef, SortingState } from '@tanstack/react-table';
import { ExternalLink, MapPin, User, Calendar, Info } from 'lucide-react';
import axios from 'axios';
import { DataTable } from '@/components/ui/data-table';
import { MapContainer, TileLayer, CircleMarker, Tooltip as LeafletTooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

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
    startDate?: string;
    completionDate?: string;
    locations?: any[];
    investigator?: string;
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
    onDataUpdate?: (data: Trial[]) => void;
}

const statusStyles: Record<string, string> = {
    // User specified statuses
    'recruiting': 'bg-emerald-500/10 text-emerald-600 dark:bg-[#2dd4bf]/20 dark:text-[#2dd4bf]',
    'not yet recruiting': 'bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400',
    'enrolling by invitation': 'bg-blue-500/10 text-blue-600 dark:bg-[#0ea5e9]/20 dark:text-[#0ea5e9]',
    'available': 'bg-teal-500/10 text-teal-600 dark:bg-teal-500/20 dark:text-teal-400',
    'approved for marketing': 'bg-indigo-500/10 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400',

    // Common fallbacks/others that might appear
    'active, not recruiting': 'bg-slate-500/20 text-slate-600 dark:text-slate-400',
    'completed': 'bg-slate-500/10 text-slate-500 dark:bg-slate-600/20 dark:text-slate-500',
    'terminated': 'bg-red-500/10 text-red-600 dark:bg-red-500/20 dark:text-red-400',
    'withdrawn': 'bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400',
    'suspended': 'bg-orange-500/10 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400',
    'unknown': 'bg-slate-500/10 text-slate-500 dark:bg-slate-600/20 dark:text-slate-500',
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
            // Normalize status to lowercase for styling lookup
            const originalStatus = row.original.status || 'unknown';
            const statusKey = originalStatus.toLowerCase();

            return (
                <div className="flex items-center justify-center w-full">
                    <span className={`inline-flex items-center justify-center gap-1.5 px-3 py-1 rounded-full text-sm font-bold uppercase tracking-tighter whitespace-nowrap ${statusStyles[statusKey] || statusStyles.unknown}`}>
                        {originalStatus}
                    </span>
                </div>
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
                return (
                    <div className="flex items-center justify-center w-full">
                        <span className="text-sm bg-slate-100 text-slate-500 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700 px-2 py-0.5 rounded-full font-bold uppercase tracking-tight">NA</span>
                    </div>
                );
            }
            return (
                <div className="flex flex-wrap items-center justify-center gap-1 max-w-[180px] mx-auto">
                    {types.map((type, i) => (
                        <span key={i} className="text-sm bg-indigo-500/10 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-400 px-2 py-0.5 rounded-full font-bold uppercase tracking-tight whitespace-nowrap">
                            {type.replace(/_/g, ' ').toLowerCase() === 'na' ? 'NA' : type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                    ))}
                </div>
            );
        },
    },
    {
        accessorKey: 'phase',
        header: 'Phase',
        size: 100,
        cell: ({ row }) => (
            <div className="flex items-center justify-center w-full">
                <span className="text-sm text-slate-700 dark:text-slate-400 font-medium">{row.original.phase}</span>
            </div>
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
                <div className="flex items-center justify-center w-full">
                    <span className={`text-sm px-2.5 py-1 rounded-full uppercase font-bold tracking-tight whitespace-nowrap ${studyTypeStyles[styleKey] || studyTypeStyles.unknown}`}>
                        {type}
                    </span>
                </div>
            );
        },
    },
    {
        accessorKey: 'lastUpdated',
        header: 'Last Updated',
        size: 120,
        cell: ({ row }) => (
            <div className="flex items-center justify-center w-full">
                <span className="text-sm text-slate-600 dark:text-slate-400">{row.original.lastUpdated}</span>
            </div>
        ),
    },
];

export function TrialsTable({ filters, onDataUpdate }: TrialsTableProps) {
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

    // Notify parent of data changes
    useEffect(() => {
        onDataUpdate?.(processedTrials);
    }, [processedTrials, onDataUpdate]);

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

    const renderExpandedContent = (trial: Trial) => {
        const validCoords = (trial.locations || [])
            .map(l => l.geoPoint)
            .filter(g => g && g.lat && g.lon);

        return (
            <div className="px-6 py-6 space-y-8 bg-muted/5 animate-in fade-in slide-in-from-top-2 duration-300">
                {/* Header Info / Timeline */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-border/50">
                    <div className="flex items-center gap-6">
                        <div className="space-y-1 text-left">
                            <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest flex items-center gap-1.5">
                                <Calendar className="h-3 w-3" /> Study Period
                            </span>
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-semibold text-foreground">
                                    {trial.startDate ? new Date(trial.startDate).toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) : 'Unknown'}
                                </span>
                                <div className="h-px w-8 bg-border" />
                                <span className="text-sm font-semibold text-foreground">
                                    {trial.completionDate ? new Date(trial.completionDate).toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) : 'Ongoing'}
                                </span>
                            </div>
                        </div>

                        <div className="h-10 w-px bg-border hidden md:block" />

                        <div className="space-y-1 text-left">
                            <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest flex items-center gap-1.5">
                                <User className="h-3 w-3" /> Principal Investigator
                            </span>
                            <div className="text-sm font-semibold text-foreground">
                                {trial.investigator || 'Not Specified'}
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        {trial.url && (
                            <a
                                href={trial.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 bg-primary/10 hover:bg-primary/20 text-primary text-xs font-bold px-4 py-2.5 rounded-lg transition-all"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <ExternalLink className="h-3.5 w-3.5" />
                                Study Details
                            </a>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 text-left">
                    {/* Main Content Area: Summary + Eligibility (Float Layout) */}
                    <div className="lg:col-span-8 block">
                        {/* Eligibility Criteria - Floated Right on Desktop */}
                        <div className="lg:float-right lg:w-1/2 lg:ml-8 lg:mb-4 w-full mb-6">
                            <div className="bg-background/40 p-4 rounded-xl border border-border/30 shadow-sm">
                                <h4 className="text-xs font-bold uppercase text-primary tracking-widest flex items-center gap-2 mb-4">
                                    <Info className="h-3.5 w-3.5" /> Eligibility Criteria
                                </h4>
                                {trial.eligibility && trial.eligibility.length > 0 ? (
                                    <ul className="space-y-3">
                                        {trial.eligibility.slice(0, 6).map((item, i) => (
                                            <li key={i} className="flex items-start gap-2.5 text-xs text-muted-foreground font-medium">
                                                <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
                                                <span>{typeof item === 'string' ? item : JSON.stringify(item)}</span>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-xs text-muted-foreground italic">No criteria details available.</p>
                                )}
                            </div>
                        </div>

                        {/* Summary Text - Wraps around floated element */}
                        <div className="space-y-6">
                            <div className="space-y-3">
                                <h4 className="text-xs font-bold uppercase text-primary tracking-widest flex items-center gap-2">
                                    <Info className="h-3.5 w-3.5" /> Summary
                                </h4>
                                <p className="text-sm text-muted-foreground leading-relaxed font-medium text-justify">
                                    {trial.summary || 'No summary available for this trial.'}
                                </p>
                            </div>

                            {trial.genes && trial.genes.length > 0 && (
                                <div className="space-y-3 pt-2 clear-both">
                                    <h4 className="text-xs font-bold uppercase text-primary tracking-widest">
                                        Genetic Targets
                                    </h4>
                                    <div className="flex flex-wrap gap-2">
                                        {trial.genes.map(g => (
                                            <span key={g} className="text-[10px] font-bold bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded uppercase">
                                                {g}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Mini Map */}
                    <div className="lg:col-span-4 space-y-4">
                        <h4 className="text-xs font-bold uppercase text-primary tracking-widest flex items-center gap-2">
                            <MapPin className="h-3.5 w-3.5" /> Study Locations ({trial.locations?.length || 0})
                        </h4>
                        <div className="h-[250px] rounded-xl overflow-hidden border border-border bg-secondary/20 relative z-0">
                            {validCoords.length > 0 ? (
                                <MapContainer
                                    center={[validCoords[0].lat, validCoords[0].lon]}
                                    zoom={3}
                                    style={{ height: '100%', width: '100%' }}
                                    scrollWheelZoom={false}
                                    zoomControl={false}
                                    attributionControl={false}
                                >
                                    <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
                                    {validCoords.map((loc, i) => (
                                        <CircleMarker
                                            key={i}
                                            center={[loc.lat, loc.lon]}
                                            pathOptions={{ color: '#19c3e6', fillColor: '#19c3e6', fillOpacity: 0.8 }}
                                            radius={4}
                                        >
                                            <LeafletTooltip direction="top" opacity={1}>
                                                <span className="text-[10px] font-bold">Site Location</span>
                                            </LeafletTooltip>
                                        </CircleMarker>
                                    ))}
                                </MapContainer>
                            ) : (
                                <div className="h-full w-full flex flex-col items-center justify-center text-center p-6 space-y-2">
                                    <MapPin className="h-8 w-8 text-muted-foreground/30" />
                                    <p className="text-[10px] text-muted-foreground italic leading-tight">
                                        Geographic coordinates not available for this study's sites.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

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
