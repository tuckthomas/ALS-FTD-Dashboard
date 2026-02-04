import { TrendingUp, FlaskConical, Link, ArrowRight, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

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
    const navigate = useNavigate();
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



    const handleMarkerClick = (geneName: string) => {
        navigate(`/gene/${encodeURIComponent(geneName)}`);
    };

    return (
        <div className="glass-panel p-6 rounded-xl">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-md font-bold text-foreground">Genetic Markers</h3>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </div>

            <div className="space-y-3">
                {markerData.map((marker) => (
                    <div
                        key={marker.name}
                        className="group cursor-pointer rounded-lg border border-primary/20 bg-slate-100 dark:bg-primary/5 transition-all flex items-stretch shadow-sm hover:-translate-y-1 hover:shadow-lg hover:shadow-primary/20 relative hover:z-10"
                        onClick={() => handleMarkerClick(marker.name)}
                    >
                        <div className="flex-1 p-3">
                            <div className="flex justify-between items-start mb-1">
                                <span className={`text-sm font-bold tracking-tight ${marker.isPrimary ? 'text-primary' : 'text-foreground'}`}>
                                    {marker.name}
                                </span>
                            </div>
                            <p className="text-[10px] text-muted-foreground leading-tight">
                                {marker.description}
                            </p>
                            <div className="flex items-center gap-4 mt-2">
                                <div className="flex items-center gap-1">
                                    <FlaskConical className="h-3 w-3 text-muted-foreground" />
                                    <span className="text-[10px] text-muted-foreground">{marker.trials} Trials</span>
                                </div>
                                <div className="flex items-center gap-1 transition-colors">
                                    <Link className="h-3 w-3 text-muted-foreground transition-colors" />
                                    <span className="text-[10px] text-muted-foreground transition-colors">{marker.drugs} Drugs</span>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center justify-center px-2">
                            <ChevronRight className="h-6 w-6 text-muted-foreground/50 group-hover:text-primary transition-all group-hover:translate-x-1 stroke-[3]" />
                        </div>
                    </div>
                ))}
            </div>

            <button 
                onClick={() => navigate('/genes')}
                className="w-full mt-4 py-2 text-xs font-semibold text-muted-foreground hover:text-primary transition-colors flex items-center justify-center gap-2"
            >
                View All Markers
                <ArrowRight className="h-4 w-4" />
            </button>
        </div>
    );
}
