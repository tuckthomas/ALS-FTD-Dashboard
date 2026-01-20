import { useState } from 'react';
import { Plus, Trash2, Play, Download, Loader2 } from 'lucide-react';
import axios from 'axios';
import { DataTable } from '@/components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';

interface FilterRow {
    id: string;
    field: string;
    operator: string;
    value: string;
}

interface QueryResult {
    [key: string]: unknown;
}

// Allowed fields for querying
const ALLOWED_FIELDS = [
    { value: 'nct_id', label: 'NCT ID' },
    { value: 'brief_title', label: 'Title' },
    { value: 'overall_status', label: 'Status' },
    { value: 'study_phase', label: 'Phase' },
    { value: 'lead_sponsor_name', label: 'Sponsor' },
    { value: 'enrollment_count', label: 'Enrollment' },
    { value: 'study_start_date', label: 'Start Date' },
    { value: 'genes', label: 'Genes' },
    { value: 'study_location', label: 'Location' },
];

const OPERATORS = [
    { value: 'equals', label: 'equals' },
    { value: 'contains', label: 'contains' },
    { value: 'starts_with', label: 'starts with' },
    { value: 'gt', label: 'greater than' },
    { value: 'lt', label: 'less than' },
    { value: 'gte', label: '≥' },
    { value: 'lte', label: '≤' },
];

export function QueryBuilderPage() {
    const [filters, setFilters] = useState<FilterRow[]>([
        { id: '1', field: 'overall_status', operator: 'equals', value: 'RECRUITING' }
    ]);
    const [logic, setLogic] = useState<'AND' | 'OR'>('AND');
    const [results, setResults] = useState<QueryResult[]>([]);
    const [columns, setColumns] = useState<ColumnDef<QueryResult>[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [resultCount, setResultCount] = useState<number | null>(null);

    const addFilter = () => {
        setFilters([...filters, {
            id: Date.now().toString(),
            field: 'brief_title',
            operator: 'contains',
            value: ''
        }]);
    };

    const removeFilter = (id: string) => {
        if (filters.length > 1) {
            setFilters(filters.filter(f => f.id !== id));
        }
    };

    const updateFilter = (id: string, key: keyof FilterRow, value: string) => {
        setFilters(filters.map(f => f.id === id ? { ...f, [key]: value } : f));
    };

    const executeQuery = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post('/api/analytics/query', {
                filters: filters.map(f => ({
                    field: f.field,
                    operator: f.operator,
                    value: f.value
                })),
                logic,
                limit: 100
            });

            const data = response.data.results;
            setResults(data);
            setResultCount(response.data.total_count);

            // Generate columns from first result
            if (data.length > 0) {
                const cols: ColumnDef<QueryResult>[] = Object.keys(data[0]).map(key => ({
                    accessorKey: key,
                    header: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    cell: ({ row }) => {
                        const val = row.getValue(key);
                        if (val === null || val === undefined) return <span className="text-slate-400 dark:text-slate-600">—</span>;
                        if (typeof val === 'object') return <span className="text-xs">{JSON.stringify(val)}</span>;
                        return <span className="text-sm">{String(val)}</span>;
                    }
                }));
                setColumns(cols);
            }
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Query failed';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const exportCSV = () => {
        if (results.length === 0) return;

        const headers = Object.keys(results[0]);
        const csvContent = [
            headers.join(','),
            ...results.map(row =>
                headers.map(h => {
                    const val = row[h];
                    if (val === null || val === undefined) return '';
                    if (typeof val === 'object') return `"${JSON.stringify(val).replace(/"/g, '""')}"`;
                    return `"${String(val).replace(/"/g, '""')}"`;
                }).join(',')
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `query_results_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="flex flex-col gap-6 p-6 max-w-[1600px] mx-auto w-full">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-foreground tracking-tight">Query Builder</h1>
                <p className="text-muted-foreground text-sm mt-1">
                    Build custom queries to explore trial data without writing SQL
                </p>
            </div>

            {/* Query Builder Card */}
            <div className="glass-panel rounded-xl p-6 space-y-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
                        <svg className="w-5 h-5 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z" />
                        </svg>
                        Filters
                    </h2>
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground uppercase">Logic:</span>
                        <button
                            onClick={() => setLogic('AND')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${logic === 'AND'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-muted-foreground hover:text-foreground'
                                }`}
                        >
                            AND
                        </button>
                        <button
                            onClick={() => setLogic('OR')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${logic === 'OR'
                                ? 'bg-accent text-accent-foreground'
                                : 'bg-secondary text-muted-foreground hover:text-foreground'
                                }`}
                        >
                            OR
                        </button>
                    </div>
                </div>

                {/* Filter Rows */}
                <div className="space-y-3">
                    {filters.map((filter, index) => (
                        <div key={filter.id} className="flex items-center gap-3">
                            {index > 0 && (
                                <span className={`text-xs font-bold px-2 py-1 rounded ${logic === 'AND' ? 'bg-primary/20 text-primary' : 'bg-accent/20 text-accent'
                                    }`}>
                                    {logic}
                                </span>
                            )}
                            <select
                                value={filter.field}
                                onChange={(e) => updateFilter(filter.id, 'field', e.target.value)}
                                className="bg-background border border-border focus:border-primary rounded-lg px-3 py-2 text-sm text-foreground"
                            >
                                {ALLOWED_FIELDS.map(f => (
                                    <option key={f.value} value={f.value}>{f.label}</option>
                                ))}
                            </select>
                            <select
                                value={filter.operator}
                                onChange={(e) => updateFilter(filter.id, 'operator', e.target.value)}
                                className="bg-background border border-border focus:border-primary rounded-lg px-3 py-2 text-sm text-foreground"
                            >
                                {OPERATORS.map(o => (
                                    <option key={o.value} value={o.value}>{o.label}</option>
                                ))}
                            </select>
                            <input
                                type="text"
                                value={filter.value}
                                onChange={(e) => updateFilter(filter.id, 'value', e.target.value)}
                                placeholder="Enter value..."
                                className="flex-1 bg-background border border-border focus:border-primary rounded-lg px-3 py-2 text-sm text-foreground"
                            />
                            <button
                                onClick={() => removeFilter(filter.id)}
                                disabled={filters.length === 1}
                                className={`p-2 rounded-lg transition-colors ${filters.length === 1
                                    ? 'text-muted-foreground cursor-not-allowed'
                                    : 'text-muted-foreground hover:text-destructive hover:bg-destructive/10'
                                    }`}
                            >
                                <Trash2 className="h-4 w-4" />
                            </button>
                        </div>
                    ))}
                </div>

                <div className="flex items-center gap-3 pt-2">
                    <button
                        onClick={addFilter}
                        className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 border border-border rounded-lg text-sm text-foreground transition-colors"
                    >
                        <Plus className="h-4 w-4" />
                        Add Filter
                    </button>
                    <div className="flex-1" />
                    <button
                        onClick={exportCSV}
                        disabled={results.length === 0}
                        className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 border border-border rounded-lg text-sm text-foreground transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Download className="h-4 w-4" />
                        Export CSV
                    </button>
                    <button
                        onClick={executeQuery}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-primary to-accent hover:opacity-90 rounded-lg text-sm font-bold text-white transition-all"
                    >
                        {isLoading ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                            <Play className="h-4 w-4" />
                        )}
                        Run Query
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Results */}
            {resultCount !== null && (
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-bold text-foreground">
                        Results <span className="text-muted-foreground font-normal">({resultCount.toLocaleString()} total)</span>
                    </h2>
                </div>
            )}

            {results.length > 0 && (
                <DataTable
                    columns={columns}
                    data={results}
                    searchPlaceholder="Filter results..."
                />
            )}
        </div>
    );
}
