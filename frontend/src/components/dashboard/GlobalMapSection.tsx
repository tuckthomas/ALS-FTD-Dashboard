interface RegionData {
    name: string;
    trials: number;
}

interface GlobalMapSectionProps {
    regions?: RegionData[];
}

export function GlobalMapSection({ regions }: GlobalMapSectionProps) {
    const defaultRegions: RegionData[] = [
        { name: 'North America', trials: 542 },
        { name: 'Europe', trials: 411 },
        { name: 'Asia Pacific', trials: 298 },
    ];

    const regionData = regions || defaultRegions;

    return (
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden h-[400px]">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#19c3e6]/5 via-transparent to-[#9338db]/5 pointer-events-none" />

            {/* Header */}
            <div className="relative z-10 flex justify-between items-center mb-4">
                <div>
                    <h3 className="text-lg font-bold text-white">Global Trial Density Map</h3>
                    <p className="text-slate-500 text-xs">Geographic hotspots for recruiting Phase III trials</p>
                </div>
                <div className="flex gap-2">
                    <div className="flex items-center gap-1.5 bg-[#0e1315]/60 px-3 py-1 rounded border border-[#19c3e6]/10">
                        <div className="w-2 h-2 rounded-full bg-[#19c3e6] animate-pulse" />
                        <span className="text-[10px] text-slate-300 uppercase tracking-tighter">High Density</span>
                    </div>
                </div>
            </div>

            {/* Map placeholder with hotspots */}
            <div className="flex items-center justify-center h-full pb-10">
                <div className="relative w-full max-w-3xl aspect-[2/1] bg-center bg-no-repeat bg-contain map-glow">
                    {/* World map outline - simplified SVG */}
                    <svg
                        viewBox="0 0 800 400"
                        className="w-full h-full opacity-30"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1"
                    >
                        {/* Simplified continent outlines */}
                        <path className="text-slate-600" d="M150,120 Q180,100 220,110 Q260,100 280,130 Q300,150 290,180 Q260,200 220,190 Q180,200 160,170 Q140,140 150,120 Z" />
                        <path className="text-slate-600" d="M320,100 Q380,80 450,90 Q520,100 540,140 Q530,180 480,200 Q420,220 360,200 Q310,170 320,100 Z" />
                        <path className="text-slate-600" d="M550,100 Q620,90 680,110 Q720,140 710,180 Q680,220 620,220 Q560,200 550,150 Q540,110 550,100 Z" />
                        <path className="text-slate-600" d="M400,240 Q450,220 500,240 Q520,280 480,320 Q420,340 380,300 Q360,260 400,240 Z" />
                        <path className="text-slate-600" d="M600,280 Q650,260 700,280 Q720,320 680,350 Q620,360 580,330 Q560,300 600,280 Z" />
                    </svg>

                    {/* Simulated Hotspots */}
                    {/* North America */}
                    <div className="absolute top-[30%] left-[20%] w-12 h-12 bg-[#19c3e6]/20 rounded-full blur-xl animate-pulse" />
                    <div className="absolute top-[30%] left-[22%] w-3 h-3 bg-[#19c3e6] rounded-full shadow-[0_0_10px_#19c3e6]" />

                    {/* Europe */}
                    <div className="absolute top-[25%] left-[50%] w-8 h-8 bg-[#9338db]/20 rounded-full blur-lg" />
                    <div className="absolute top-[26%] left-[51%] w-2 h-2 bg-[#9338db] rounded-full shadow-[0_0_10px_#9338db]" />

                    {/* Asia Pacific */}
                    <div className="absolute top-[40%] left-[80%] w-16 h-16 bg-[#19c3e6]/10 rounded-full blur-2xl" />
                    <div className="absolute top-[42%] left-[82%] w-3 h-3 bg-[#19c3e6] rounded-full shadow-[0_0_10px_#19c3e6]" />
                </div>
            </div>

            {/* Region stats */}
            <div className="absolute bottom-6 left-6 flex gap-8">
                {regionData.map((region) => (
                    <div key={region.name} className="flex flex-col">
                        <span className="text-[10px] text-slate-500 uppercase tracking-widest">{region.name}</span>
                        <span className="text-sm font-bold text-white">{region.trials} Trials</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
