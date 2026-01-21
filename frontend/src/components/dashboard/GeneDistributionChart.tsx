import { useState, useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { GeneData } from '../../pages/DashboardPage';
import { Dna } from 'lucide-react';

interface GeneDistributionChartProps {
    data: GeneData[];
}

type FilterType = 'all' | 'interventional' | 'observational';

const COLORS = [
    '#3b82f6', // blue-500
    '#10b981', // emerald-500
    '#8b5cf6', // violet-500
    '#f59e0b', // amber-500
    '#ef4444', // red-500
    '#ec4899', // pink-500
    '#06b6d4', // cyan-500
    '#84cc16', // lime-500
];

export function GeneDistributionChart({ data = [] }: GeneDistributionChartProps) {
    const [filter, setFilter] = useState<FilterType>('all');

    const chartData = useMemo(() => {
        if (!data) return [];
        return data
            .map(gene => ({
                name: gene.name,
                value: filter === 'all'
                    ? gene.trials
                    : filter === 'interventional'
                        ? (gene.interventional || 0)
                        : (gene.observational || 0),
                full_name: gene.full_name
            }))
            .filter(item => item.value > 0) // Hide segments with 0 value
            .sort((a, b) => b.value - a.value)
            .slice(0, 8); // Top 8 genes for readability
    }, [data, filter]);

    return (
        <div className="glass-panel p-6 rounded-xl h-[350px] flex flex-col">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <Dna className="h-5 w-5 text-primary" />
                        <h3 className="text-lg font-bold text-foreground">Gene Distribution</h3>
                    </div>
                    <p className="text-muted-foreground text-xs">Trials by genetic marker</p>
                </div>

                <div className="flex bg-muted/50 p-1 rounded-lg">
                    {(['all', 'interventional', 'observational'] as const).map((type) => (
                        <button
                            key={type}
                            onClick={() => setFilter(type)}
                            className={`
                                px-3 py-1 rounded-md text-[10px] font-medium transition-all capitalize uppercase tracking-wide
                                ${filter === type
                                    ? 'bg-background text-foreground shadow-sm'
                                    : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}
                            `}
                        >
                            {type}
                        </button>
                    ))}
                </div>
            </div>

            <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={2}
                            dataKey="value"
                        >
                            {chartData.map((_entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                borderColor: 'hsl(var(--border))',
                                borderRadius: '0.5rem',
                                color: 'hsl(var(--foreground))'
                            }}
                            itemStyle={{ color: 'hsl(var(--foreground))' }}
                            formatter={(value: number | undefined) => [`${value} trials`, 'Count']}
                        />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="circle"
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            <div className="mt-2 text-center">
                <p className="text-[10px] text-muted-foreground italic">
                    Showing top {chartData.length} genes ({filter})
                </p>
            </div>
        </div>
    );
}
