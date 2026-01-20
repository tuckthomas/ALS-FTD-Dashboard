import { Terminal } from 'lucide-react';

export function Footer() {
    return (
        <footer className="max-w-[1600px] mx-auto px-6 py-8 border-t border-[#19c3e6]/5 mt-6 mb-4">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                {/* System Status */}
                <div className="flex items-center gap-8">

                    <div className="flex flex-col">
                        <span className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-bold tracking-widest">
                            Last Data Ingest
                        </span>
                        <span className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                            14 mins ago
                        </span>
                    </div>
                </div>

                {/* Security Badges */}
                <div className="flex gap-4">

                    <div className="px-4 py-2 rounded-lg border border-black/5 dark:border-white/5 bg-black/5 dark:bg-white/5 text-slate-700 dark:text-slate-400 text-xs font-bold flex items-center gap-2">
                        <Terminal className="h-4 w-4" />
                        API access
                    </div>
                </div>
            </div>
        </footer>
    );
}
