import { Info } from 'lucide-react';

interface TrialStatusData {
    recruiting: number;
    active: number;
    completed: number;
    withdrawn: number;
    total: number;
}

interface TrialStatusChartProps {
    data?: TrialStatusData;
}

export function TrialStatusChart({ data }: TrialStatusChartProps) {
    const defaultData: TrialStatusData = {
        recruiting: 42,
        active: 32,
        completed: 16,
        withdrawn: 10,
        total: 1284,
    };

    const chartData = data || defaultData;

    // Calculate stroke dash offsets for SVG donut chart
    const circumference = 2 * Math.PI * 40; // r=40
    const recruitingOffset = circumference * (1 - chartData.recruiting / 100);
    const activeOffset = circumference * (1 - (chartData.recruiting + chartData.active) / 100);
    const completedOffset = circumference * (1 - (chartData.recruiting + chartData.active + chartData.completed) / 100);

    return (
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h3 className="text-lg font-bold text-white">Trial Status Distribution</h3>
                    <p className="text-slate-500 text-xs">Current operational phases across global registry</p>
                </div>
                <Info className="h-5 w-5 text-slate-500" />
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
                            className="text-slate-800"
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
                        <span className="text-3xl font-bold text-white">{chartData.total.toLocaleString()}</span>
                        <span className="text-[10px] text-slate-500 uppercase">Total Trials</span>
                    </div>
                </div>

                {/* Legend */}
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-[#19c3e6]" />
                        <span className="text-xs text-slate-300">Recruiting ({chartData.recruiting}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-[#9338db]/60" />
                        <span className="text-xs text-slate-300">Active ({chartData.active}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-500/40" />
                        <span className="text-xs text-slate-300">Completed ({chartData.completed}%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-slate-700" />
                        <span className="text-xs text-slate-300">Withdrawn ({chartData.withdrawn}%)</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
