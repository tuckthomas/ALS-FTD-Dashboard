

interface FilterCheckboxProps {
    label: string;
    checked?: boolean;
    color?: 'blue' | 'purple' | 'teal';
}

function FilterCheckbox({ label, checked = false, color = 'blue' }: FilterCheckboxProps) {
    const colorClasses = {
        blue: 'text-[#0ea5e9] focus:ring-[#0ea5e9]',
        purple: 'text-[#a855f7] focus:ring-[#a855f7]',
        teal: 'text-[#2dd4bf] focus:ring-[#2dd4bf]',
    };

    return (
        <label className="flex items-center gap-3 py-1.5 cursor-pointer group">
            <input
                type="checkbox"
                defaultChecked={checked}
                className={`rounded border-[#334155] bg-transparent ${colorClasses[color]} focus:ring-offset-[#0f172a]`}
            />
            <span className="text-sm text-slate-300 group-hover:text-white transition-colors">
                {label}
            </span>
        </label>
    );
}

export function TrialFilters() {
    return (
        <aside className="w-72 flex-shrink-0 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-2">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <svg className="w-5 h-5 text-[#0ea5e9]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 3H2l8 9.46V19l4 2v-8.54L22 3z" />
                    </svg>
                    Filters
                </h3>
                <button className="text-xs text-[#0ea5e9] hover:text-[#a855f7] transition-colors font-medium">
                    Reset All
                </button>
            </div>

            {/* Clinical Phase */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-300 mb-2">
                    <svg className="w-4 h-4 text-[#2dd4bf]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Clinical Phase</span>
                </div>
                <div className="space-y-1">
                    <FilterCheckbox label="Phase I" checked color="blue" />
                    <FilterCheckbox label="Phase II" checked color="blue" />
                    <FilterCheckbox label="Phase III" color="blue" />
                    <FilterCheckbox label="Phase IV" color="blue" />
                </div>
            </div>

            {/* Genetic Markers */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-300 mb-2">
                    <svg className="w-4 h-4 text-[#a855f7]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 4v16M8 8l4-4 4 4M8 16l4 4 4-4" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Genetic Markers</span>
                </div>
                <div className="space-y-1">
                    <FilterCheckbox label="C9orf72 Mutation" checked color="purple" />
                    <FilterCheckbox label="SOD1 Mutation" color="purple" />
                    <FilterCheckbox label="Sporadic ALS" color="purple" />
                </div>
            </div>

            {/* Location Radius */}
            <div className="glass-panel p-4 rounded-xl space-y-4">
                <div className="flex items-center gap-2 text-slate-300">
                    <svg className="w-4 h-4 text-[#0ea5e9]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Location Radius</span>
                </div>
                <div className="space-y-4">
                    <div className="flex items-center justify-between text-xs font-mono text-[#0ea5e9]">
                        <span>0 mi</span>
                        <span>500 mi</span>
                    </div>
                    <div className="relative h-1.5 bg-[#334155] rounded-full">
                        <div className="absolute inset-0 bg-[#0ea5e9]/30 rounded-full w-3/4" />
                        <div className="absolute h-4 w-4 bg-[#0ea5e9] rounded-full -top-1.5 shadow-lg shadow-[#0ea5e9]/40 left-3/4 -translate-x-1/2 cursor-pointer border-2 border-white" />
                    </div>
                    <div className="flex flex-col gap-2">
                        <label className="text-[10px] text-slate-500 uppercase font-bold">Zip Code</label>
                        <input
                            type="text"
                            placeholder="e.g. 02138"
                            className="bg-[#0f172a] border-[#334155] focus:border-[#0ea5e9] focus:ring-1 focus:ring-[#0ea5e9] rounded px-2 py-1.5 text-xs text-white"
                        />
                    </div>
                </div>
            </div>

            {/* Primary Outcome */}
            <div className="glass-panel p-4 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-slate-300 mb-2">
                    <svg className="w-4 h-4 text-[#2dd4bf]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                    </svg>
                    <span className="text-xs font-bold uppercase tracking-wider">Primary Outcome</span>
                </div>
                <select className="w-full bg-[#1e293b] border-[#334155] focus:border-[#2dd4bf] focus:ring-1 focus:ring-[#2dd4bf] rounded-lg text-xs text-slate-300 py-2">
                    <option>All Outcomes</option>
                    <option>Survival Rate</option>
                    <option>Functional Improvement</option>
                    <option>Biomarker Reduction</option>
                    <option>Safety/Tolerability</option>
                </select>
            </div>
        </aside>
    );
}
