import { TrendingUp, FlaskConical, Link, ArrowRight } from 'lucide-react';

interface GeneticMarker {
    name: string;
    trend: { value: string; direction: 'up' | 'down' | 'stable' };
    description: string;
    trials: number;
    drugs: number;
    isPrimary?: boolean;
}

interface GeneticMarkersWidgetProps {
    markers?: GeneticMarker[];
}

export function GeneticMarkersWidget({ markers }: GeneticMarkersWidgetProps) {
    const defaultMarkers: GeneticMarker[] = [
        {
            name: 'C9orf72',
            trend: { value: '+12%', direction: 'up' },
            description: 'Hexanucleotide repeat expansions. Most common genetic cause of ALS.',
            trials: 42,
            drugs: 8,
            isPrimary: true,
        },
        {
            name: 'SOD1',
            trend: { value: '+8%', direction: 'up' },
            description: 'Superoxide dismutase 1. Classic target for antisense therapies.',
            trials: 28,
            drugs: 5,
        },
        {
            name: 'TARDBP',
            trend: { value: 'STABLE', direction: 'stable' },
            description: 'TDP-43 pathology. Critical for non-genetic ALS forms.',
            trials: 15,
            drugs: 3,
        },
        {
            name: 'FUS',
            trend: { value: '-2%', direction: 'down' },
            description: 'Fused in Sarcoma. Emerging early-onset juvenile variant.',
            trials: 12,
            drugs: 2,
        },
    ];

    const markerData = markers || defaultMarkers;

    const getTrendStyles = (direction: 'up' | 'down' | 'stable') => {
        switch (direction) {
            case 'up':
                return 'text-emerald-400 bg-emerald-400/10';
            case 'down':
                return 'text-rose-400 bg-rose-400/10';
            default:
                return 'text-slate-500 bg-slate-500/10';
        }
    };

    return (
        <div className="glass-panel p-6 rounded-xl">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-md font-bold text-white">Genetic Markers</h3>
                <TrendingUp className="h-4 w-4 text-slate-500" />
            </div>

            <div className="space-y-3">
                {markerData.map((marker) => (
                    <div
                        key={marker.name}
                        className="group cursor-pointer p-3 rounded-lg border border-transparent hover:border-[#19c3e6]/20 hover:bg-[#19c3e6]/5 transition-all"
                    >
                        <div className="flex justify-between items-start mb-1">
                            <span className={`text-sm font-bold tracking-tight ${marker.isPrimary ? 'text-[#19c3e6]' : 'text-white'}`}>
                                {marker.name}
                            </span>
                            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${getTrendStyles(marker.trend.direction)}`}>
                                {marker.trend.value}
                            </span>
                        </div>
                        <p className="text-[10px] text-slate-500 leading-tight">
                            {marker.description}
                        </p>
                        <div className="flex items-center gap-4 mt-2">
                            <div className="flex items-center gap-1">
                                <FlaskConical className="h-3 w-3 text-slate-500" />
                                <span className="text-[10px] text-slate-400">{marker.trials} Trials</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <Link className="h-3 w-3 text-slate-500" />
                                <span className="text-[10px] text-slate-400">{marker.drugs} Drugs</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <button className="w-full mt-4 py-2 text-xs font-semibold text-slate-500 hover:text-[#19c3e6] transition-colors flex items-center justify-center gap-2">
                View All Markers
                <ArrowRight className="h-4 w-4" />
            </button>
        </div>
    );
}
