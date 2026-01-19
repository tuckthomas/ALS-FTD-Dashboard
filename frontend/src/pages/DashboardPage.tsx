import { StatCard } from '../components/dashboard/StatCard';
import { TrialStatusChart } from '../components/dashboard/TrialStatusChart';
import { FundingSourcesChart } from '../components/dashboard/FundingSourcesChart';
import { GlobalMapSection } from '../components/dashboard/GlobalMapSection';
import { TrialDiscoveryWidget } from '../components/dashboard/TrialDiscoveryWidget';
import { GeneticMarkersWidget } from '../components/dashboard/GeneticMarkersWidget';
import { LiveUpdatesWidget } from '../components/dashboard/LiveUpdatesWidget';

export function DashboardPage() {
    return (
        <div className="max-w-[1600px] mx-auto p-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Main Stage (Left 9 columns) */}
                <div className="lg:col-span-9 space-y-6">
                    {/* Stats Bar */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <StatCard
                            label="Trials Observed"
                            value="1,284"
                            trend={{ value: '+5.2%', direction: 'up' }}
                        />
                        <StatCard
                            label="Participants"
                            value="42.5k"
                            trend={{ value: '+12.8%', direction: 'up' }}
                        />
                        <StatCard
                            label="Clinical Sites"
                            value="892"
                            trend={{ value: 'Stable', direction: 'stable' }}
                        />
                        <StatCard
                            label="Avg. Enrollment"
                            value="84%"
                            trend={{ value: '-2.1%', direction: 'down' }}
                        />
                    </div>

                    {/* Complex Charts Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <TrialStatusChart />
                        <FundingSourcesChart />
                    </div>

                    {/* Geographic Density Map */}
                    <GlobalMapSection />
                </div>

                {/* Right Sidebar (Right 3 columns) */}
                <aside className="lg:col-span-3 space-y-6">
                    <TrialDiscoveryWidget />
                    <GeneticMarkersWidget />
                    <LiveUpdatesWidget />
                </aside>
            </div>
        </div>
    );
}
