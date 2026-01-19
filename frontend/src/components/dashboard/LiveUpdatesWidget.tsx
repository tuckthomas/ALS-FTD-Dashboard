interface LiveUpdate {
    id: string;
    type: 'success' | 'info';
    content: React.ReactNode;
}

interface LiveUpdatesWidgetProps {
    updates?: LiveUpdate[];
}

export function LiveUpdatesWidget({ updates }: LiveUpdatesWidgetProps) {
    const defaultUpdates: LiveUpdate[] = [
        {
            id: '1',
            type: 'success',
            content: (
                <>
                    <span className="font-bold text-white">NCT04849741</span> transitioned to Phase III recruiting in Tokyo site.
                </>
            ),
        },
        {
            id: '2',
            type: 'info',
            content: (
                <>
                    New industry partner <span className="font-bold text-white">NeuroGenix</span> added for SOD1 study.
                </>
            ),
        },
    ];

    const updateData = updates || defaultUpdates;

    const getIndicatorColor = (type: 'success' | 'info') => {
        return type === 'success' ? 'bg-emerald-400' : 'bg-[#19c3e6]';
    };

    return (
        <div className="glass-panel p-5 rounded-xl">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                Live Updates
            </h3>

            <div className="space-y-4">
                {updateData.map((update) => (
                    <div key={update.id} className="flex gap-3">
                        <div className={`mt-1 w-1.5 h-1.5 rounded-full ${getIndicatorColor(update.type)} shrink-0`} />
                        <p className="text-xs text-slate-300 leading-relaxed">
                            {update.content}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}
