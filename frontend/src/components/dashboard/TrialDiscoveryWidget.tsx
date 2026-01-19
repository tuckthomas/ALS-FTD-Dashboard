import { Sparkles } from 'lucide-react';

export function TrialDiscoveryWidget() {
    return (
        <div className="glass-panel p-6 rounded-xl marker-gradient">
            <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-[#19c3e6]" />
                Trial Discovery
            </h3>

            <div className="space-y-4">
                {/* Molecular Target */}
                <div className="space-y-1.5">
                    <label className="text-[10px] uppercase text-slate-500 font-bold tracking-wider">
                        Molecular Target
                    </label>
                    <select className="w-full bg-[#0e1315] border border-[#19c3e6]/20 rounded-lg py-2 px-3 text-sm text-slate-300 focus:ring-[#19c3e6] focus:border-[#19c3e6]">
                        <option>All Markers</option>
                        <option>SOD1</option>
                        <option>C9orf72</option>
                        <option>TARDBP</option>
                    </select>
                </div>

                {/* Trial Phase */}
                <div className="space-y-1.5">
                    <label className="text-[10px] uppercase text-slate-500 font-bold tracking-wider">
                        Trial Phase
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                        <button className="py-2 px-3 bg-[#19c3e6]/10 border border-[#19c3e6]/20 rounded text-xs font-medium text-[#19c3e6]">
                            Phase II
                        </button>
                        <button className="py-2 px-3 bg-[#0e1315] border border-white/5 rounded text-xs font-medium text-slate-400 hover:border-[#19c3e6]/40 transition-colors">
                            Phase III
                        </button>
                    </div>
                </div>

                {/* Generate Button */}
                <button className="w-full py-2.5 bg-[#19c3e6] text-[#0e1315] font-bold rounded-lg text-sm mt-2 hover:bg-white transition-all shadow-lg shadow-[#19c3e6]/20">
                    Generate Report
                </button>
            </div>
        </div>
    );
}
