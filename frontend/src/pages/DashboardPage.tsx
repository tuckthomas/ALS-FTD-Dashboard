import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, History } from 'lucide-react';
import { StatCard } from '../components/dashboard/StatCard';
import { TrialStatusChart } from '../components/dashboard/TrialStatusChart';
import { FundingSourcesChart } from '../components/dashboard/FundingSourcesChart';
import { TrialsByYearChart } from '../components/dashboard/TrialsByYearChart';
import { GlobalMapSection } from '../components/dashboard/GlobalMapSection';

import { GeneticMarkersWidget } from '../components/dashboard/GeneticMarkersWidget';
import { LiveUpdatesWidget } from '../components/dashboard/LiveUpdatesWidget';
import { Switch } from '../components/ui/switch';

interface DashboardStats {
    total_trials: number;
    total_participants: number;
    clinical_sites: number;
    avg_enrollment: number;
    recruiting_percentage: number;
}

interface StatusData {
    name: string;
    value: number;
    raw_status?: string;
}

interface FundingData {
    name: string;
    value: number;
    percentage: number;
}

interface GeoData {
    name: string;
    value: number;
}

interface GeneData {
    name: string;
    full_name: string;
    category: string;
    trials: number;
    drugs: number;
}

interface DashboardPackage {
    stats: DashboardStats;
    active_stats: DashboardStats;
    status_data: StatusData[];
    funding_data: FundingData[];
    geo_data: GeoData[];
    gene_data: GeneData[];
    year_data: any[];
    map_data: any[];
    news_data: any[];
}

export function DashboardPage() {
    const [allPackage, setAllPackage] = useState<DashboardPackage | null>(null);
    const [famPackage, setFamPackage] = useState<DashboardPackage | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isFamilial, setIsFamilial] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [allRes, famRes] = await Promise.all([
                    axios.get('/api/analytics/dashboard-package'),
                    axios.get('/api/analytics/dashboard-package', { params: { familial: true } }),
                ]);

                setAllPackage(allRes.data);
                setFamPackage(famRes.data);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch dashboard data:', err);
                setError('Failed to load dashboard data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Select the active data based on toggle
    const currentData = isFamilial ? famPackage : allPackage;

    // Format large numbers
    const formatNumber = (num: number): string => {
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
        return num.toString();
    };

    if (loading) {
        return (
            <div className="max-w-[1600px] mx-auto p-6 flex items-center justify-center min-h-[400px]">
                <div className="text-slate-400 animate-pulse">Loading dashboard data...</div>
            </div>
        );
    }

    if (error || !currentData) {
        return (
            <div className="max-w-[1600px] mx-auto p-6 flex items-center justify-center min-h-[400px]">
                <div className="text-red-400">{error || 'Data not available'}</div>
            </div>
        );
    }

    return (
        <div className="max-w-[1600px] mx-auto p-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Stage (Left 9 columns) */}
                <div className="lg:col-span-9 space-y-6">
                    {/* Section: Current Landscape */}
                    <div className="space-y-4">
                        <div className="flex items-center justify-between gap-4">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-primary/10 rounded-lg">
                                    <Activity className="h-8 w-8 text-primary" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-semibold text-foreground tracking-tight">
                                        Current Landscape
                                    </h2>
                                    <p className="text-muted-foreground italic text-sm">
                                        Real-time overview of active clinical trials and global research sites.
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center space-x-2">
                                <span className={`text-sm font-medium ${!isFamilial ? 'text-foreground' : 'text-muted-foreground'}`}>All</span>
                                <Switch checked={isFamilial} onCheckedChange={setIsFamilial} />
                                <span className={`text-sm font-medium ${isFamilial ? 'text-foreground' : 'text-muted-foreground'}`}>Familial</span>
                            </div>
                        </div>

                        {/* Active Stats Bar */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <StatCard
                                label="Active Trials"
                                value={formatNumber(currentData.active_stats.total_trials)}
                                trend={{ value: 'Live', direction: 'stable' }}
                            />
                            <StatCard
                                label="Active Participants"
                                value={formatNumber(currentData.active_stats.total_participants)}
                                trend={{ value: 'Interventional Trials', direction: 'stable' }}
                            />
                            <StatCard
                                label="Active Sites"
                                value={formatNumber(currentData.active_stats.clinical_sites)}
                                trend={{ value: 'Interventional Trials', direction: 'stable' }}
                            />
                            <StatCard
                                label="Recruiting Rate"
                                value={`${currentData.active_stats.recruiting_percentage}%`}
                                trend={{ value: 'Interventional Trials', direction: 'stable' }}
                            />
                        </div>

                        {/* Geographic Density Map */}
                        <GlobalMapSection data={currentData.map_data} />
                    </div>

                    {/* Section: Historical Trends */}
                    <div className="space-y-4 pt-4">
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-primary/10 rounded-lg">
                                <History className="h-8 w-8 text-primary" />
                            </div>
                            <div>
                                <h2 className="text-xl font-semibold text-foreground tracking-tight">
                                    Historical Trends
                                </h2>
                                <p className="text-muted-foreground italic text-sm">
                                    Long-term analysis of trial volume, funding sources, and enrollment data.
                                </p>
                            </div>
                        </div>

                        {/* Historical Stats Bar */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <StatCard
                                label="Total Trials"
                                value={formatNumber(currentData.stats.total_trials)}
                                trend={{ value: 'All Time', direction: 'stable' }}
                            />
                            <StatCard
                                label="Total Participants"
                                value={formatNumber(currentData.stats.total_participants)}
                                trend={{ value: 'All Time', direction: 'stable' }}
                            />
                            <StatCard
                                label="Total Sites"
                                value={formatNumber(currentData.stats.clinical_sites)}
                                trend={{ value: 'All Time', direction: 'stable' }}
                            />
                            <StatCard
                                label="Median Enrollment"
                                value={formatNumber(currentData.stats.avg_enrollment)}
                                trend={{ value: 'Per Trial', direction: 'stable' }}
                            />
                        </div>

                        {/* Timeline Chart */}
                        <div className="w-full">
                            <TrialsByYearChart data={currentData.year_data} />
                        </div>

                        {/* Complex Charts Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <TrialStatusChart data={currentData.status_data} />
                            <FundingSourcesChart data={currentData.funding_data} />
                        </div>
                    </div>
                </div>

                {/* Right Sidebar (Right 3 columns) */}
                <aside className="lg:col-span-3 space-y-6">

                    <LiveUpdatesWidget news={currentData.news_data} />
                    <GeneticMarkersWidget markers={currentData.gene_data.map(g => ({
                        name: g.name,
                        trend: { value: `${g.trials} trials`, direction: 'stable' as const },
                        description: g.full_name,
                        trials: g.trials,
                        drugs: g.drugs,
                    }))} />
                </aside>
            </div>
        </div>
    );
}