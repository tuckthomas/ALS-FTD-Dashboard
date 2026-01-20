interface FundingItem {
    name: string;
    value: number;
    percentage: number;
}

interface FundingSourcesChartProps {
    data?: FundingItem[];
}

const colorMap: Record<string, string> = {
    'NIH/Federal': 'from-[#19c3e6]/40 to-[#19c3e6]',
    'Industry': 'from-[#9338db]/40 to-[#9338db]',
    'Academic': 'from-[#19c3e6]/20 to-[#19c3e6]/40',
    'Other': 'from-slate-600 to-slate-500',
};

export function FundingSourcesChart({ data }: FundingSourcesChartProps) {
    const defaultData: FundingItem[] = [
        { name: 'NIH/Federal', value: 0, percentage: 42 },
        { name: 'Industry', value: 0, percentage: 38 },
        { name: 'Academic', value: 0, percentage: 14 },
        { name: 'Other', value: 0, percentage: 6 },
    ];

    const chartData = data && data.length > 0 ? data : defaultData;

    return (
        <div className="glass-panel p-6 rounded-xl">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="font-semibold text-foreground">Active Trials by Sponsor Type</h3>
                    <p className="text-sm text-muted-foreground">Breakdown of trial sponsorship volume</p>
                </div>
                <button className="text-primary text-xs font-semibold hover:underline">
                    Export CSV
                </button>
            </div>

            <div className="space-y-6 pt-4">
                {chartData.map((source) => (
                    <div key={source.name} className="space-y-2">
                        <div className="flex justify-between text-xs mb-1">
                            <span className="text-muted-foreground">{source.name}</span>
                            <span className="font-bold text-foreground">{source.percentage}%</span>
                        </div>
                        <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${colorMap[source.name] || 'from-slate-600 to-slate-500'} rounded-full transition-all duration-500`}
                                style={{ width: `${source.percentage}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
