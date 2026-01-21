import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Calendar, Filter } from 'lucide-react';

interface Filters {
    genes: string[];
    startDate: string; // YYYY-MM-DD
    endDate: string;   // YYYY-MM-DD
}

interface NewsFiltersProps {
    onFiltersChange: (filters: Filters) => void;
}

interface FilterCheckboxProps {
    label: string;
    checked?: boolean;
    onChange?: (checked: boolean) => void;
}

function FilterCheckbox({ label, checked = false, onChange }: FilterCheckboxProps) {
    return (
        <label className="flex items-center gap-3 py-1.5 cursor-pointer group">
            <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onChange?.(e.target.checked)}
                className="rounded-md border-border bg-transparent text-[#a855f7] focus:ring-[#a855f7] focus:ring-offset-background"
            />
            <span className="text-sm text-slate-700 dark:text-slate-400 group-hover:text-foreground transition-colors font-medium">
                {label}
            </span>
        </label>
    );
}

export function NewsFilters({ onFiltersChange }: NewsFiltersProps) {
    const [genes, setGenes] = useState<string[]>([]);
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    
    const [geneOptions, setGeneOptions] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOptions = async () => {
            try {
                // Fetch gene options from the same endpoint used for trial filters
                const response = await axios.get('/api/analytics/filter-options');
                setGeneOptions(response.data.genes || []);
            } catch (error) {
                console.error("Failed to fetch gene options for news filters:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchOptions();
    }, []);

    // Notify parent component of filter changes
    useEffect(() => {
        onFiltersChange({
            genes,
            startDate,
            endDate
        });
    }, [genes, startDate, endDate, onFiltersChange]);

    const toggleGene = (gene: string) => {
        setGenes(prev =>
            prev.includes(gene)
                ? prev.filter(g => g !== gene)
                : [...prev, gene]
        );
    };

    const resetAll = () => {
        setGenes([]);
        setStartDate('');
        setEndDate('');
    };

    if (loading) {
        return (
            <aside className="w-72 flex-shrink-0 flex flex-col gap-6 p-4">
                <div className="flex items-center gap-2 text-slate-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Loading filters...</span>
                </div>
            </aside>
        );
    }

    return (
        <aside className="w-72 flex-shrink-0 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-2 h-[calc(100vh-100px)] sticky top-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                    <Filter className="w-5 h-5 text-primary" />
                    Filters
                </h3>
                <button
                    onClick={resetAll}
                    className="text-xs text-[#0ea5e9] hover:text-[#a855f7] transition-colors font-medium"
                >
                    Reset All
                </button>
            </div>

            {/* Date Range Filter */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <Calendar className="w-4 h-4 text-primary" />
                    <span className="text-xs font-bold uppercase tracking-wider">Date Range</span>
                </div>
                <div className="space-y-2">
                    <div className="flex flex-col gap-1">
                        <label className="text-[10px] uppercase text-muted-foreground font-semibold">Start Date</label>
                        <input 
                            type="date" 
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className="w-full bg-secondary/50 border border-input rounded px-2 py-1.5 text-xs text-foreground focus:ring-1 focus:ring-primary outline-none"
                        />
                    </div>
                    <div className="flex flex-col gap-1">
                        <label className="text-[10px] uppercase text-muted-foreground font-semibold">End Date</label>
                        <input 
                            type="date" 
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className="w-full bg-secondary/50 border border-input rounded px-2 py-1.5 text-xs text-foreground focus:ring-1 focus:ring-primary outline-none"
                        />
                    </div>
                </div>
            </div>

            {/* Genetic Markers Filter */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 4v16M8 8l4-4 4 4M8 16l4 4 4 4" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Genetic Markers</span>
                </div>
                <div className="space-y-1">
                    {geneOptions.map((gene) => (
                        <FilterCheckbox
                            key={gene}
                            label={gene}
                            checked={genes.includes(gene)}
                            onChange={() => toggleGene(gene)}
                        />
                    ))}
                </div>
            </div>
        </aside>
    );
}