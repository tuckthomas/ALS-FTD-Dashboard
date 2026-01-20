import { Info } from 'lucide-react';

interface StatusItem {
    name: string;
    value: number;
    raw_status?: string;
}

interface TrialStatusChartProps {
    data?: StatusItem[];
}

export function TrialStatusChart({ data }: TrialStatusChartProps) {
    // Calculate totals and percentages from data
    const total = data?.reduce((sum, item) => sum + item.value, 0) || 0;

    // Map status names to display categories
    const getPercentage = (names: string[]): number => {
        if (!data || total === 0) return 0;
        const count = data
            .filter(item => names.some(n => item.name.toLowerCase().includes(n.toLowerCase())))
            .reduce((sum, item) => sum + item.value, 0);
        return Math.round((count / total) * 100);
    };

    const recruiting = getPercentage(['Recruiting', 'Enrolling']);
    const active = getPercentage(['Active', 'Not Recruiting']);
    const completed = getPercentage(['Completed']);

    // Calculate stroke dash offsets for SVG donut chart
    const circumference = 2 * Math.PI * 40; // r=40
    const recruitingOffset = circumference * (1 - recruiting / 100);
    const activeOffset = circumference * (1 - (recruiting + active) / 100);
    const completedOffset = circumference * (1 - (recruiting + active + completed) / 100);

    return (
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-lg font-bold text-foreground">Trial Status Distribution</h3>
                    <p className="text-muted-foreground text-xs">Current operational phases across global registry</p>
                </div>
                <Info className="h-5 w-5 text-muted-foreground" />
            </div>

            <div className="flex items-center justify-around h-64">
                {/* Donut Chart */}
                <div className="relative w-48 h-48">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                        {/* Background circle */}
                        <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="transparent"
                            stroke="currentColor"
                            strokeWidth="8"
                            className="text-muted/20"
                        />
                        {/* Recruiting segment */}
                        <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="transparent"
                            stroke="#19c3e6"
                            strokeWidth="8"
                            strokeDasharray={circumference}
                            strokeDashoffset={recruitingOffset}
                        />
                        {/* Active segment */}
                        <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="transparent"
                            stroke="rgba(147, 56, 219, 0.6)"
                            strokeWidth="8"
                            strokeDasharray={circumference}
                            strokeDashoffset={activeOffset}
                        />
                        {/* Completed segment */}
                        <circle
                            cx="50"
                            cy="50"
                            r="40"
                            fill="transparent"
                            stroke="rgba(34, 197, 94, 0.4)"
                            strokeWidth="8"
                            strokeDasharray={circumference}
                            strokeDashoffset={completedOffset}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold text-foreground">{total.toLocaleString()}</span>
                        <span className="text-[10px] text-muted-foreground uppercase">Total Trials</span>
                    </div>
                </div>

                {/* Legend */}
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-[#19c3e6]" />
                        <span className="text-xs text-muted-foreground">Recruiting ({recruiting}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-[#9338db]/60" />
                        <span className="text-xs text-muted-foreground">Active ({active}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-500/40" />
                        <span className="text-xs text-muted-foreground">Completed ({completed}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-slate-700" />
                        <span className="text-xs text-muted-foreground">Other ({100 - recruiting - active - completed}%)</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
