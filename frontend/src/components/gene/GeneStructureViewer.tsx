import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface GeneStructureViewerProps {
    payload: {
        gene: {
            symbol: string;
            name?: string;
        };
        structure: {
            id: number;
            source_type: string;
            external_id: string;
            title?: string;
            componentProps: Record<string, string>;
        };
    };
}

export function GeneStructureViewer({ payload }: GeneStructureViewerProps) {
    const key = useMemo(() => {
        const p = payload.structure.componentProps;
        // Remount whenever the underlying load target changes
        return `${payload.structure.source_type}:${payload.structure.external_id}:${p['molecule-id'] || ''}:${p['custom-data-url'] || ''}`;
    }, [payload]);

    return (
        <Card className="w-full h-full flex flex-col overflow-hidden border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader className="py-4 px-6 border-b border-border/50 bg-muted/20">
                <CardTitle className="text-lg font-medium flex items-center gap-2">
                    <span className="font-bold text-primary">{payload.gene.symbol}</span>
                    <span className="text-muted-foreground font-normal text-sm">
                        {payload.structure.title ? `— ${payload.structure.title}` : '— 3D Structure'}
                    </span>
                    {payload.structure.source_type === 'alphafold' && (
                        <span className="ml-auto text-xs bg-indigo-500/10 text-indigo-400 px-2 py-1 rounded border border-indigo-500/20">
                            AlphaFold Predicted
                        </span>
                    )}
                    {payload.structure.source_type === 'pdb' && (
                        <span className="ml-auto text-xs bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded border border-emerald-500/20">
                            Experimental (PDB)
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0 flex-1 relative min-h-[500px] bg-black/5">
                {/* 
                  The pdbe-molstar component is loaded globally via CDN in index.html.
                  We use React.createElement to bypass JSX type checking for this web component.
                */}
                {React.createElement('pdbe-molstar', {
                    key,
                    className: 'w-full h-full absolute inset-0 block',
                    ...payload.structure.componentProps,
                })}
            </CardContent>
        </Card>
    );
}

