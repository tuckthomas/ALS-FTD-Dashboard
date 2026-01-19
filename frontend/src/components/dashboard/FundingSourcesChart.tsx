interface FundingSource {
    name: string;
    percentage: number;
    color: string;
}

interface FundingSourcesChartProps {
    data?: FundingSource[];
}

export function FundingSourcesChart({ data }: FundingSourcesChartProps) {
    const defaultData: FundingSource[] = [
        { name: 'NIH / Federal', percentage: 42, color: 'from-[#19c3e6]/40 to-[#19c3e6]' },
        { name: 'Industry (Pharma)', percentage: 38, color: 'from-[#9338db]/40 to-[#9338db]' },
        { name: 'Academic / Foundations', percentage: 14, color: 'from-[#19c3e6]/20 to-[#19c3e6]/40' },
        { name: 'Philanthropic', percentage: 6, color: 'from-slate-600 to-slate-500' },
    ];

    const chartData = data || defaultData;

    return (
        <div className="glass-panel p-6 rounded-xl">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-lg font-bold text-white">Primary Funding Sources</h3>
                    <p className="text-slate-500 text-xs">Analysis of capital injection by sector</p>
                </div>
                <button className="text-[#19c3e6] text-xs font-semibold hover:underline">
                    Export CSV
                </button>
            </div>

            <div className="space-y-6 pt-4">
                {chartData.map((source) => (
                    <div key={source.name} className="space-y-2">
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-slate-300">{source.name}</span>
                            <span className="font-bold text-white">{source.percentage}%</span>
                        </div>
                        <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${source.color} rounded-full transition-all duration-500`}
                                style={{ width: `${source.percentage}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
