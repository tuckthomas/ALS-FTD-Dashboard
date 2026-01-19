import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface Trial {
    id: string;
    nctId: string;
    title: string;
    sponsor: string;
    status: 'recruiting' | 'active' | 'completed';
    phase: string;
    focus: string;
    lastUpdated: string;
    summary?: string;
    eligibility?: string[];
}

const mockTrials: Trial[] = [
    {
        id: '1',
        nctId: 'NCT02623699',
        title: 'Tofersen Long-term Extension in SOD1-ALS',
        sponsor: 'Biogen',
        status: 'recruiting',
        phase: 'Phase III',
        focus: 'Antisense Oligonucleotide',
        lastUpdated: 'Oct 12, 2023',
    },
    {
        id: '2',
        nctId: 'NCT04297683',
        title: 'HEALEY ALS Platform Trial - Regimen G',
        sponsor: 'MGH Neurology',
        status: 'recruiting',
        phase: 'Phase II/III',
        focus: 'Platform Study',
        lastUpdated: 'Nov 04, 2023',
        summary: 'This regimen evaluates the safety and efficacy of ABBV-CLS-726, a therapeutic antibody, in patients with Amyotrophic Lateral Sclerosis (ALS). The HEALEY ALS Platform Trial is designed to evaluate multiple investigational treatments simultaneously to accelerate the development of effective therapies.',
        eligibility: [
            'Sporadic or Familial ALS diagnosis',
            'Symptoms onset < 36 months',
            'SVC ≥ 50% of predicted',
        ],
    },
    {
        id: '3',
        nctId: 'NCT03280056',
        title: 'NurOwn® in ALS Patients - Phase III',
        sponsor: 'BrainStorm Cell Therapeutics',
        status: 'active',
        phase: 'Phase III',
        focus: 'Cell Therapy',
        lastUpdated: 'Sep 28, 2023',
    },
    {
        id: '4',
        nctId: 'NCT04165824',
        title: 'Study of Oral Edaravone in ALS',
        sponsor: 'Mitsubishi Tanabe',
        status: 'completed',
        phase: 'Phase III',
        focus: 'Small Molecule',
        lastUpdated: 'Oct 30, 2023',
    },
];

export function TrialsTable() {
    const [expandedId, setExpandedId] = useState<string | null>('2');

    const getStatusBadge = (status: Trial['status']) => {
        const styles = {
            recruiting: 'bg-[#2dd4bf]/20 text-[#2dd4bf]',
            active: 'bg-slate-500/20 text-slate-400',
            completed: 'bg-[#0ea5e9]/20 text-[#0ea5e9]',
        };
        const labels = {
            recruiting: 'Recruiting',
            active: 'Active, Not Recruiting',
            completed: 'Completed',
        };
        return (
            <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter ${styles[status]}`}>
                {status === 'recruiting' && (
                    <span className="h-1.5 w-1.5 rounded-full bg-[#2dd4bf] animate-pulse" />
                )}
                {labels[status]}
            </span>
        );
    };

    return (
        <div className="flex-1 flex flex-col glass-panel rounded-xl overflow-hidden">
            <div className="overflow-x-auto custom-scrollbar flex-1">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-[#334155] bg-white/5">
                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                                Trial Title & Identifier
                            </th>
                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                                Status
                            </th>
                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                                Phase
                            </th>
                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                                Primary Focus
                            </th>
                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-500">
                                Last Updated
                            </th>
                            <th className="px-6 py-4"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-[#334155]/50">
                        {mockTrials.map((trial) => (
                            <>
                                <tr
                                    key={trial.id}
                                    className={`group cursor-pointer transition-colors ${expandedId === trial.id
                                        ? 'bg-[#0ea5e9]/5 border-l-4 border-[#0ea5e9]'
                                        : 'hover:bg-[#0ea5e9]/5'
                                        }`}
                                    onClick={() => setExpandedId(expandedId === trial.id ? null : trial.id)}
                                >
                                    <td className="px-6 py-4">
                                        <div className="flex flex-col">
                                            <span className={`text-sm font-bold transition-colors ${expandedId === trial.id ? 'text-[#0ea5e9]' : 'text-white group-hover:text-[#0ea5e9]'
                                                }`}>
                                                {trial.title}
                                            </span>
                                            <span className="text-[10px] font-mono text-slate-500 mt-1 uppercase">
                                                {trial.nctId} | {trial.sponsor}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">{getStatusBadge(trial.status)}</td>
                                    <td className="px-6 py-4">
                                        <span className="text-sm text-slate-300 font-medium">{trial.phase}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-xs text-slate-400 bg-[#1e293b] px-2 py-0.5 rounded">
                                            {trial.focus}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-xs text-slate-400">{trial.lastUpdated}</span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        {expandedId === trial.id ? (
                                            <ChevronUp className="h-5 w-5 text-[#0ea5e9]" />
                                        ) : (
                                            <ChevronDown className="h-5 w-5 text-slate-600 group-hover:text-[#0ea5e9] transition-all" />
                                        )}
                                    </td>
                                </tr>
                                {expandedId === trial.id && trial.summary && (
                                    <tr key={`${trial.id}-expanded`} className="bg-[#0ea5e9]/5">
                                        <td colSpan={6} className="px-12 py-6 border-t border-[#0ea5e9]/20">
                                            <div className="grid grid-cols-3 gap-8">
                                                <div className="col-span-2 space-y-4">
                                                    <h4 className="text-xs font-bold uppercase text-slate-500 tracking-widest">
                                                        Study Summary
                                                    </h4>
                                                    <p className="text-sm text-slate-300 leading-relaxed">
                                                        {trial.summary}
                                                    </p>
                                                    <div className="flex gap-4 pt-2">
                                                        <button className="bg-[#0ea5e9]/20 hover:bg-[#0ea5e9]/30 text-[#0ea5e9] text-xs font-bold px-4 py-2 rounded-lg transition-colors border border-[#0ea5e9]/30">
                                                            Detailed Protocol
                                                        </button>
                                                        <button className="bg-white/10 hover:bg-white/20 text-white text-xs font-bold px-4 py-2 rounded-lg transition-colors">
                                                            Contact PI
                                                        </button>
                                                    </div>
                                                </div>
                                                {trial.eligibility && (
                                                    <div className="space-y-4">
                                                        <h4 className="text-xs font-bold uppercase text-slate-500 tracking-widest">
                                                            Eligibility Highlight
                                                        </h4>
                                                        <ul className="space-y-2">
                                                            {trial.eligibility.map((item, i) => (
                                                                <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                                                                    <svg className="w-4 h-4 text-[#2dd4bf] shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                                                                        <polyline points="22,4 12,14.01 9,11.01" />
                                                                    </svg>
                                                                    {item}
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="border-t border-[#334155] bg-white/5 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-500">Rows per page:</span>
                    <select className="bg-[#1e293b] border-[#334155] focus:border-[#0ea5e9] rounded text-xs text-slate-300 py-1">
                        <option>10</option>
                        <option selected>25</option>
                        <option>50</option>
                    </select>
                </div>
                <div className="flex items-center gap-6">
                    <span className="text-xs text-slate-400">Page 1 of 4</span>
                    <div className="flex gap-2">
                        <button className="p-1.5 rounded border border-[#334155] bg-[#1e293b] text-slate-500 cursor-not-allowed">
                            <ChevronDown className="h-4 w-4 rotate-90" />
                        </button>
                        <button className="p-1.5 rounded border border-[#334155] bg-[#1e293b] text-white hover:bg-[#334155] hover:text-[#0ea5e9] transition-colors">
                            <ChevronDown className="h-4 w-4 -rotate-90" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
