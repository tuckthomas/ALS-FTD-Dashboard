import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts';
import { Activity, Users, FileText } from 'lucide-react';
import axios from 'axios';

// --- Types ---
interface SummaryStats {
    total_trials: number;
    active_trials: number;
    total_enrollment: number;
}

interface ChartData {
    name: string;
    value: number;
    [key: string]: string | number;
}

// --- Components ---

const StatCard = ({ title, value, icon: Icon, description }: { title: string, value: string | number, icon: any, description?: string }) => (
    <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{title}</CardTitle>
            <Icon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
            <div className="text-2xl font-bold">{value}</div>
            <p className="text-xs text-muted-foreground">{description}</p>
        </CardContent>
    </Card>
);

const AnalyticsDashboard: React.FC = () => {
    const [summary, setSummary] = useState<SummaryStats | null>(null);
    const [phaseData, setPhaseData] = useState<ChartData[]>([]);
    const [statusData, setStatusData] = useState<ChartData[]>([]);
    const [loading, setLoading] = useState(true);

    const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/api';

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [summaryRes, phaseRes, statusRes] = await Promise.all([
                    axios.get(`${API_BASE_URL}/analytics/summary`),
                    axios.get(`${API_BASE_URL}/analytics/trials-by-phase`),
                    axios.get(`${API_BASE_URL}/analytics/trials-by-status`),
                ]);

                setSummary(summaryRes.data);
                setPhaseData(phaseRes.data);
                setStatusData(statusRes.data);
            } catch (error) {
                console.error("Failed to fetch analytics data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

    if (loading) {
        return <div className="p-10 flex justify-center text-white">Loading Dashboard...</div>;
    }

    return (
        <div className="flex-1 space-y-4 p-8 pt-6 min-h-screen bg-background text-foreground">
            <div className="flex items-center justify-between space-y-2">
                <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
            </div>

            {/* Stats Row */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatCard
                    title="Total Trials"
                    value={summary?.total_trials || 0}
                    icon={FileText}
                    description="All protocols"
                />
                <StatCard
                    title="Active Trials"
                    value={summary?.active_trials || 0}
                    icon={Activity}
                    description="Recruiting"
                />
                <StatCard
                    title="Enrollment"
                    value={summary?.total_enrollment.toLocaleString() || 0}
                    icon={Users}
                    description="Participants"
                />
            </div>

            {/* Charts Row */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                {/* Bar Chart */}
                <Card className="col-span-4">
                    <CardHeader>
                        <CardTitle>Overview</CardTitle>
                    </CardHeader>
                    <CardContent className="pl-2">
                        <div className="h-[350px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={statusData}>
                                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" vertical={false} />
                                    <XAxis
                                        dataKey="name"
                                        stroke="#888888"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(val) => val.substring(0, 3)}
                                    />
                                    <YAxis
                                        stroke="#888888"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(value) => `${value}`}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', color: 'hsl(var(--foreground))' }}
                                    />
                                    <Bar dataKey="value" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>

                {/* Pie Chart */}
                <Card className="col-span-3">
                    <CardHeader>
                        <CardTitle>Phases</CardTitle>
                        <CardDescription>
                            Distribution by Phase
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[350px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={phaseData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {phaseData.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }} />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default AnalyticsDashboard;
