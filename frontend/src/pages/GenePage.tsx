import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Dna, Newspaper, ExternalLink, Calendar, ChevronRight, FlaskConical, Tag } from 'lucide-react';
import { TrialsTable } from '@/components/trials/TrialsTable';

interface GeneData {
    gene_symbol: string;
    gene_name: string;
    gene_risk_category: string;
}

interface StructureData {
    gene: {
        symbol: string;
        name: string;
    };
    structure: {
        id: number;
        source_type: string;
        external_id: string;
        title: string;
        componentProps: Record<string, string>;
    };
}

interface NewsArticle {
    id: number;
    title: string;
    source_name: string;
    url: string;
    publication_date: string;
    tags: string[];
}



export function GenePage() {
    const { symbol } = useParams<{ symbol: string }>();
    const [gene, setGene] = useState<GeneData | null>(null);
    const [structure, setStructure] = useState<StructureData | null>(null);
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!symbol) return;

        const loadData = async () => {
            setLoading(true);
            try {
                // Gene details
                const geneRes = await axios.get(`/api/trials/genes/${symbol}`);
                setGene(geneRes.data);

                // 3D Structure
                try {
                    const structRes = await axios.get(`/api/trials/genes/${symbol}/structure`);
                    setStructure(structRes.data);
                } catch {
                    setStructure(null);
                }

                // News for gene
                try {
                    const newsRes = await axios.get(`/api/trials/news?genes=${symbol}&limit=3`);
                    setNews(newsRes.data);
                } catch {
                    setNews([]);
                }
            } catch (err) {
                console.error('Failed to load gene data:', err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [symbol]);

    const riskStyle = (cat: string) => {
        const c = cat?.toLowerCase();
        if (c?.includes('definitive')) return 'bg-green-500/10 text-green-400';
        if (c === 'moderate') return 'bg-yellow-500/10 text-yellow-400';
        if (c === 'limited') return 'bg-orange-500/10 text-orange-400';
        return 'bg-slate-500/10 text-slate-400';
    };

    if (loading) {
        return (
            <div className="max-w-[1600px] mx-auto p-6">
                <div className="h-[400px] flex items-center justify-center text-muted-foreground animate-pulse">
                    Loading gene data...
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-[1600px] mx-auto p-6 space-y-6">
            {/* Page Header */}
            <div className="flex items-center gap-3">
                <h1 className="text-3xl font-bold tracking-tight">{symbol}</h1>
                <span className="text-sm bg-secondary px-3 py-1 rounded-full text-muted-foreground">Gene</span>
            </div>

            {/* Top Row: Gene Info + 3D Viewer */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Gene Overview */}
                <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2">
                            <Dna className="h-5 w-5 text-primary" />
                            Gene Overview
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <div className="text-sm text-muted-foreground">Symbol</div>
                            <div className="text-xl font-bold text-primary">{gene?.gene_symbol}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted-foreground">Full Name</div>
                            <div className="font-medium">{gene?.gene_name || 'Unknown'}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted-foreground">Risk Category</div>
                            <span className={`inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${riskStyle(gene?.gene_risk_category || '')}`}>
                                {gene?.gene_risk_category || 'Unknown'}
                            </span>
                        </div>
                    </CardContent>
                </Card>

                {/* 3D Structure Viewer */}
                <div className="lg:col-span-2">
                    <Card className="h-full min-h-[400px] border-border/50 bg-card/50 backdrop-blur-sm overflow-hidden">
                        <CardHeader className="py-3 border-b border-border/50">
                            <CardTitle className="text-base flex items-center gap-2">
                                <span className="text-primary font-bold">{symbol}</span>
                                <span className="text-muted-foreground font-normal">— 3D Structure</span>
                                {structure?.structure.source_type === 'alphafold' && (
                                    <span className="ml-auto text-xs bg-indigo-500/10 text-indigo-400 px-2 py-1 rounded">AlphaFold</span>
                                )}
                                {structure?.structure.source_type === 'pdb' && (
                                    <span className="ml-auto text-xs bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded">PDB</span>
                                )}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0 h-[350px] relative bg-black/20">
                            {structure ? (
                                React.createElement('pdbe-molstar', {
                                    key: `${structure.structure.source_type}:${structure.structure.external_id}`,
                                    className: 'w-full h-full absolute inset-0 block',
                                    ...structure.structure.componentProps,
                                })
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
                                    <Dna className="h-12 w-12 opacity-30 mb-3" />
                                    <p className="text-sm">No 3D structure available for {symbol}</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Trials Section */}
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                <CardHeader className="pb-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <FlaskConical className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <CardTitle>Clinical Trials</CardTitle>
                            <CardDescription>All active studies targeting {symbol}</CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="pt-0">
                    <TrialsTable filters={{ genes: symbol ? [symbol] : [] }} />
                </CardContent>
            </Card>

            {/* News Section */}
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
                <CardHeader className="flex flex-row items-center justify-between pb-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Newspaper className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                            <CardTitle>Recent News</CardTitle>
                            <CardDescription>Latest research updates for {symbol}</CardDescription>
                        </div>
                    </div>
                    <Link to="/news" className="text-sm font-medium text-primary hover:underline flex items-center gap-1">
                        View All <ChevronRight className="h-4 w-4" />
                    </Link>
                </CardHeader>
                <CardContent>
                    {news.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {news.map((article) => (
                                <a
                                    key={article.id}
                                    href={article.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="group p-4 rounded-xl bg-secondary/30 hover:bg-secondary/50 border border-border/30 hover:border-primary/30 transition-all"
                                >
                                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                                        {article.source_name}
                                    </span>
                                    <h4 className="font-semibold text-sm mt-1 group-hover:text-primary transition-colors line-clamp-2">
                                        {article.title}
                                    </h4>
                                    <div className="flex items-center justify-between text-xs text-muted-foreground mt-3">
                                        <span className="flex items-center gap-1">
                                            <Calendar className="h-3 w-3" />
                                            {new Date(article.publication_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                        </span>
                                        <span className="flex items-center gap-1 text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                                            Read <ExternalLink className="h-3 w-3" />
                                        </span>
                                    </div>
                                    {article.tags.length > 0 && (
                                        <div className="flex flex-wrap gap-1 mt-2">
                                            {article.tags.slice(0, 2).map((tag, i) => (
                                                <span key={i} className="text-[9px] bg-background/50 px-1.5 py-0.5 rounded flex items-center gap-0.5">
                                                    <Tag className="h-2 w-2" />{tag}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </a>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-muted-foreground">
                            <Newspaper className="h-8 w-8 mx-auto mb-2 opacity-30" />
                            <p className="text-sm">No recent news for {symbol}</p>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
