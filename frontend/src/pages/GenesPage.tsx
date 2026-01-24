import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Dna, Search, ChevronRight } from 'lucide-react';

interface GeneItem {
    symbol: string;
    name: string;
    risk_category: string;
}

const riskCategoryColors: Record<string, string> = {
    'Definitive ALS gene': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-500/30',
    'Strong evidence': 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-500/30',
    'Moderate evidence': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-500/30',
    'Clinical modifier': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-500/30',
    'Tenuous': 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-500/30',
};

export function GenesPage() {
    const [genes, setGenes] = useState<GeneItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchGenes = async () => {
            try {
                setLoading(true);
                const response = await axios.get('/api/genes/');
                // API returns array of [symbol, name, risk_category]
                const geneList: GeneItem[] = response.data.map((g: [string, string, string]) => ({
                    symbol: g[0],
                    name: g[1],
                    risk_category: g[2],
                }));
                setGenes(geneList);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch genes:', err);
                setError('Failed to load gene data');
            } finally {
                setLoading(false);
            }
        };

        fetchGenes();
    }, []);

    const filteredGenes = genes.filter(gene =>
        gene.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        gene.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        gene.risk_category.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Group by risk category for display
    const definitiveGenes = filteredGenes.filter(g => g.risk_category === 'Definitive ALS gene');
    const strongGenes = filteredGenes.filter(g => g.risk_category === 'Strong evidence');
    const moderateGenes = filteredGenes.filter(g => g.risk_category === 'Moderate evidence');
    const otherGenes = filteredGenes.filter(g =>
        !['Definitive ALS gene', 'Strong evidence', 'Moderate evidence'].includes(g.risk_category)
    );

    const renderGeneCard = (gene: GeneItem) => (
        <Link
            key={gene.symbol}
            to={`/gene/${gene.symbol}`}
            className="group block"
        >
            <div className="p-4 rounded-lg border border-border/50 bg-card/50 hover:bg-secondary/30 hover:border-primary/30 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5">
                <div className="flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-primary text-lg">{gene.symbol}</span>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full border ${riskCategoryColors[gene.risk_category] || riskCategoryColors['Tenuous']}`}>
                                {gene.risk_category}
                            </span>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">{gene.name}</p>
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                </div>
            </div>
        </Link>
    );

    const renderSection = (title: string, geneList: GeneItem[], accentColor: string) => {
        if (geneList.length === 0) return null;
        return (
            <div className="space-y-3">
                <h3 className={`text-sm font-semibold uppercase tracking-wider ${accentColor}`}>
                    {title} ({geneList.length})
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {geneList.map(renderGeneCard)}
                </div>
            </div>
        );
    };

    return (
        <div className="max-w-[1600px] mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
                        <Dna className="h-8 w-8 text-primary" />
                        Gene Database
                    </h1>
                    <p className="text-muted-foreground mt-1">
                        Browse ALS and FTD associated genes
                    </p>
                </div>

                {/* Search */}
                <div className="relative w-full md:w-80">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search genes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    />
                </div>
            </div>

            {loading ? (
                <div className="h-[400px] flex items-center justify-center text-muted-foreground animate-pulse">
                    Loading genes...
                </div>
            ) : error ? (
                <div className="h-[400px] flex items-center justify-center text-red-400">
                    {error}
                </div>
            ) : (
                <div className="space-y-8">
                    {/* Stats Card */}
                    <Card className="bg-gradient-to-r from-primary/5 to-transparent border-primary/20">
                        <CardContent className="py-4">
                            <div className="flex flex-wrap gap-6 text-sm">
                                <div>
                                    <span className="text-muted-foreground">Total Genes:</span>
                                    <span className="ml-2 font-bold text-foreground">{genes.length}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Definitive:</span>
                                    <span className="ml-2 font-bold text-green-500">{genes.filter(g => g.risk_category === 'Definitive ALS gene').length}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Strong Evidence:</span>
                                    <span className="ml-2 font-bold text-emerald-500">{genes.filter(g => g.risk_category === 'Strong evidence').length}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Moderate Evidence:</span>
                                    <span className="ml-2 font-bold text-yellow-500">{genes.filter(g => g.risk_category === 'Moderate evidence').length}</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {filteredGenes.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            No genes found matching "{searchTerm}"
                        </div>
                    ) : (
                        <>
                            {renderSection('Definitive ALS Genes', definitiveGenes, 'text-green-500')}
                            {renderSection('Strong Evidence', strongGenes, 'text-emerald-500')}
                            {renderSection('Moderate Evidence', moderateGenes, 'text-yellow-500')}
                            {renderSection('Other Genes', otherGenes, 'text-slate-400')}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
