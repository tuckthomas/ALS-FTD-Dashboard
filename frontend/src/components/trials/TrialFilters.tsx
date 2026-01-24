import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { getFilterOptions, getCachedFilterOptions } from '@/lib/filterOptionsCache';

interface Filters {
    phases: string[];
    genes: string[];
    status: string;
    studyType: string;
    interventionTypes: string[];
    search: string;
}

interface TrialFiltersProps {
    onFiltersChange?: (filters: Filters) => void;
    initialFilters?: Partial<Filters>;
}

interface FilterCheckboxProps {
    label: string;
    checked?: boolean;
    color?: 'blue' | 'purple' | 'teal';
    onChange?: (checked: boolean) => void;
}

function FilterCheckbox({ label, checked = false, color = 'blue', onChange }: FilterCheckboxProps) {
    const colorClasses = {
        blue: 'text-[#0ea5e9] focus:ring-[#0ea5e9]',
        purple: 'text-[#a855f7] focus:ring-[#a855f7]',
        teal: 'text-[#2dd4bf] focus:ring-[#2dd4bf]',
    };

    return (
        <label className="flex items-center gap-3 py-1.5 cursor-pointer group">
            <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onChange?.(e.target.checked)}
                className={`rounded-md border-border bg-transparent ${colorClasses[color]} focus:ring-offset-background`}
            />
            <span className="text-sm text-slate-700 dark:text-slate-400 group-hover:text-foreground transition-colors font-medium">
                {label}
            </span>
        </label>
    );
}

export function TrialFilters({ onFiltersChange, initialFilters }: TrialFiltersProps) {
    const [phases, setPhases] = useState<string[]>(initialFilters?.phases || []);
    const [genes, setGenes] = useState<string[]>(initialFilters?.genes || []);
    const [status, setStatus] = useState<string>(initialFilters?.status || '');
    const [studyType, setStudyType] = useState<string>(initialFilters?.studyType || '');
    const [interventionTypes, setInterventionTypes] = useState<string[]>(initialFilters?.interventionTypes || []);

    // Dynamic Options State - use cached data
    const [options, setOptions] = useState<{
        phases: string[];
        study_types: string[];
        statuses: string[];
        genes: string[];
        intervention_types: string[];
    }>(() => {
        // Check for cached options on mount
        const cached = getCachedFilterOptions();
        return cached || {
            phases: [],
            study_types: [],
            statuses: [],
            genes: [],
            intervention_types: []
        };
    });
    const [loading, setLoading] = useState(() => !getCachedFilterOptions());

    useEffect(() => {
        // If cached, no need to fetch
        if (getCachedFilterOptions()) {
            return;
        }

        const fetchOptions = async () => {
            const data = await getFilterOptions();
            setOptions(data);
            setLoading(false);
        };
        fetchOptions();
    }, []);

    const togglePhase = (phase: string) => {
        setPhases(prev =>
            prev.includes(phase)
                ? prev.filter(p => p !== phase)
                : [...prev, phase]
        );
    };

    const toggleGene = (gene: string) => {
        setGenes(prev =>
            prev.includes(gene)
                ? prev.filter(g => g !== gene)
                : [...prev, gene]
        );
    };

    const toggleInterventionType = (type: string) => {
        setInterventionTypes(prev =>
            prev.includes(type)
                ? prev.filter(t => t !== type)
                : [...prev, type]
        );
    };

    const resetAll = () => {
        setPhases([]);
        setGenes([]);
        setStatus('');
        setStudyType('');
        setInterventionTypes([]);
    };

    // Notify parent of filter changes
    useEffect(() => {
        onFiltersChange?.({
            phases,
            genes,
            status,
            studyType,
            interventionTypes,
            search: '',
        });
    }, [phases, genes, status, studyType, interventionTypes, onFiltersChange]);

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
        <aside className="w-72 flex-shrink-0 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-2">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                    <svg className="w-5 h-5 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z" />
                    </svg>
                    Filters
                </h3>
                <button
                    onClick={resetAll}
                    className="text-xs text-[#0ea5e9] hover:text-[#a855f7] transition-colors font-medium"
                >
                    Reset All
                </button>
            </div>

            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Clinical Phase</span>
                </div>
                <div className="space-y-1">
                    {options.phases.map((phase) => (
                        <FilterCheckbox
                            key={phase}
                            label={phase || "N/A"}
                            checked={phases.includes(phase)}
                            onChange={() => togglePhase(phase)}
                            color="blue"
                        />
                    ))}
                </div>
            </div>
            {/* Study Type */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Study Type</span>
                </div>
                <div className="space-y-1">
                    {options.study_types.map((type) => (
                        <FilterCheckbox
                            key={type}
                            label={type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            checked={studyType === type}
                            onChange={() => setStudyType(prev => prev === type ? '' : type)}
                            color="blue"
                        />
                    ))}
                </div>
            </div>

            {/* Intervention Type */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Intervention Type</span>
                </div>
                <div className="space-y-1">
                    {options.intervention_types.length > 0 ? (
                        options.intervention_types.map((type) => (
                            <FilterCheckbox
                                key={type}
                                label={type}
                                checked={interventionTypes.includes(type)}
                                onChange={() => toggleInterventionType(type)}
                                color="purple"
                            />
                        ))
                    ) : (
                        <span className="text-xs text-slate-400 italic pl-2">None available</span>
                    )}
                </div>
            </div>

            {/* Recruitment Status */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Recruitment Status</span>
                </div>
                <div className="space-y-1">
                    {options.statuses.map((s) => (
                        <FilterCheckbox
                            key={s}
                            label={s}
                            checked={status === s}
                            onChange={() => setStatus(prev => prev === s ? '' : s)}
                            color="teal"
                        />
                    ))}
                </div>
            </div>

            {/* Genetic Markers */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 4v16M8 8l4-4 4 4M8 16l4 4 4 4" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Genetic Markers</span>
                </div>
                <div className="space-y-1">
                    {options.genes.map((gene) => (
                        <FilterCheckbox
                            key={gene}
                            label={gene}
                            checked={genes.includes(gene)}
                            onChange={() => toggleGene(gene)}
                            color="purple"
                        />
                    ))}
                </div>
            </div>

            {/* Location Radius */}
            <div className="glass-panel p-4 rounded-xl space-y-4">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Location Radius</span>
                </div>
                <div className="space-y-4">
                    <div className="flex items-center justify-between text-xs font-mono text-primary">
                        <span>0 mi</span>
                        <span>500 mi</span>
                    </div>
                    <div className="relative h-1.5 bg-secondary rounded-full">
                        <div className="absolute inset-0 bg-primary/30 rounded-full w-3/4" />
                        <div className="absolute h-4 w-4 bg-primary rounded-full -top-1.5 shadow-lg shadow-primary/40 left-3/4 -translate-x-1/2 cursor-pointer border-2 border-background" />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label className="text-[10px] text-slate-700 dark:text-slate-400 uppercase font-bold">Zip Code</label>
                        <input
                            type="text"
                            placeholder="e.g. 02138"
                            className="bg-secondary/50 border-input focus:border-primary focus:ring-1 focus:ring-primary rounded px-2 py-1.5 text-xs text-foreground"
                        />
                    </div>
                </div>
            </div>

            {/* Primary Outcome */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-400 mb-2">
                    <svg className="w-4 h-4 text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Primary Outcome</span>
                </div>
                <select className="w-full bg-secondary/50 border-input focus:border-primary focus:ring-1 focus:ring-primary rounded-lg text-xs text-foreground py-2">
                    <option>All Outcomes</option>
                    <option>Survival Rate</option>
                    <option>Functional Improvement</option>
                    <option>Biomarker Reduction</option>
                    <option>Safety/Tolerability</option>
                </select>
            </div>
        </aside >
    );
}
