import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

interface YearData {
    year: number;
    count: number;
}

interface TrialsByYearChartProps {
    data?: YearData[];
    filters?: {
        status?: string;
        phase?: string;
        country?: string;
        familial?: boolean;
    };
}

export function TrialsByYearChart({ data: propData, filters }: TrialsByYearChartProps) {
    const [data, setData] = useState<YearData[]>(propData || []);
    const [isLoading, setIsLoading] = useState(!propData);

    useEffect(() => {
        if (propData) {
            setData(propData);
            setIsLoading(false);
            return;
        }

        const fetchData = async () => {
            try {
                const params = new URLSearchParams();
                if (filters?.status && filters.status !== 'all') params.append('status', filters.status);
                if (filters?.phase && filters.phase !== 'all') params.append('phase', filters.phase);
                if (filters?.country && filters.country !== 'all') params.append('country', filters.country);
                if (filters?.familial) params.append('familial', 'true');

                const response = await axios.get('/api/analytics/trials-by-year', { params });
                setData(response.data);
            } catch (error) {
                console.error('Failed to fetch trials by year:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [filters, propData]);

    if (isLoading) {
        return <div className="glass-panel p-6 rounded-xl h-[350px] animate-pulse"></div>;
    }

    return (
        <div className="glass-panel p-6 rounded-xl flex flex-col h-[350px]">
            <div className="mb-6">
                <h3 className="text-lg font-bold text-foreground">Trials Started by Year</h3>
                <p className="text-sm text-muted-foreground">Number of new clinical trials initiated annually</p>
            </div>

            <div className="flex-1 w-full min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                        <XAxis
                            dataKey="year"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                            dy={10}
                        />
                        <YAxis
                            width={40}
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                        />
                        <Tooltip
                            cursor={{ fill: 'hsl(var(--muted) / 0.3)' }}
                            contentStyle={{
                                backgroundColor: 'hsl(var(--popover))',
                                borderColor: 'hsl(var(--border))',
                                color: 'hsl(var(--popover-foreground))',
                                borderRadius: 'var(--radius)',
                                fontSize: '12px'
                            }}
                            itemStyle={{ color: 'hsl(var(--foreground))' }}
                        />
                        <Bar
                            dataKey="count"
                            fill="hsl(var(--primary))"
                            radius={[4, 4, 0, 0]}
                            maxBarSize={50}
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
