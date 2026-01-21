import { useState, useEffect } from 'react';
import axios from 'axios';
import { Newspaper, Loader2, Calendar, ExternalLink, Tag, Filter } from 'lucide-react';
import { NewsFilters } from '../components/news/NewsFilters';

interface NewsArticle {
    id: number;
    title: string;
    summary: string;
    source_name: string;
    url: string;
    image_url: string | null;
    publication_date: string;
    tags: string[];
}

export function NewsPage() {
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [loading, setLoading] = useState(true);
    const [showMobileFilters, setShowMobileFilters] = useState(false);
    
    // Filter State
    const [filters, setFilters] = useState({
        genes: [] as string[],
        startDate: '',
        endDate: ''
    });

    useEffect(() => {
        const fetchNews = async () => {
            setLoading(true);
            try {
                const params = new URLSearchParams();
                
                // Add gene filters
                filters.genes.forEach(gene => params.append('genes', gene));
                
                // Add date filters
                if (filters.startDate) params.append('start_date', filters.startDate);
                if (filters.endDate) params.append('end_date', filters.endDate);
                
                // Limit
                params.append('limit', '100');

                const response = await axios.get(`/api/trials/news?${params.toString()}`);
                setArticles(response.data);
            } catch (err) {
                console.error("Failed to fetch news:", err);
            } finally {
                setLoading(false);
            }
        };
        
        // Debounce slightly to prevent rapid refetching while typing/clicking
        const timeoutId = setTimeout(() => {
            fetchNews();
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [filters]);

    return (
        <div className="flex flex-1 max-w-[1600px] mx-auto w-full gap-6 p-6">
            {/* Filters Sidebar - Desktop */}
            <div className="hidden lg:block">
                <NewsFilters onFiltersChange={setFilters} />
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col gap-6 w-full">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Newspaper className="h-8 w-8 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight text-foreground">
                                Research News & Updates
                            </h1>
                            <p className="text-muted-foreground italic text-sm mt-1">
                                Aggregating the latest breakthroughs in ALS and FTD research from global sources.
                            </p>
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                        {/* Mobile Filter Toggle */}
                        <button 
                            onClick={() => setShowMobileFilters(!showMobileFilters)}
                            className="lg:hidden p-2 bg-secondary rounded-md text-foreground"
                        >
                            <Filter className="h-5 w-5" />
                        </button>

                        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 flex items-center gap-2">
                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-xs font-bold text-emerald-500 uppercase tracking-wider">Live Feed</span>
                        </div>
                    </div>
                </div>

                {/* Mobile Filters (Collapsible) */}
                {showMobileFilters && (
                    <div className="lg:hidden glass-panel p-4 rounded-xl mb-4">
                        <NewsFilters onFiltersChange={setFilters} />
                    </div>
                )}

                {loading ? (
                    <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
                        <Loader2 className="h-12 w-12 text-primary animate-spin" />
                        <p className="text-muted-foreground animate-pulse">Fetching latest research...</p>
                    </div>
                ) : articles.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {articles.map((article) => (
                            <div key={article.id} className="glass-panel rounded-2xl overflow-hidden flex flex-col group hover:border-primary/30 transition-all hover:shadow-lg h-full">
                                {/* Image Header */}
                                <div className="h-48 overflow-hidden bg-secondary/30 relative flex-shrink-0">
                                    {article.image_url ? (
                                        <img 
                                            src={article.image_url} 
                                            alt={article.title}
                                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                            onError={(e) => {
                                                (e.target as HTMLImageElement).style.display = 'none';
                                                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
                                            }}
                                        />
                                    ) : null}
                                    <div className={`w-full h-full flex items-center justify-center absolute inset-0 bg-secondary/20 ${article.image_url ? 'hidden' : ''}`}>
                                        <Newspaper className="h-12 w-12 text-muted-foreground/20" />
                                    </div>
                                    <div className="absolute top-4 left-4">
                                        <span className="bg-background/80 backdrop-blur-md text-[10px] font-bold px-2 py-1 rounded shadow-sm text-foreground">
                                            {article.source_name}
                                        </span>
                                    </div>
                                </div>

                                {/* Content */}
                                <div className="p-6 flex-1 flex flex-col space-y-4">
                                    <div className="space-y-2">
                                        <h3 className="font-bold text-lg leading-tight group-hover:text-primary transition-colors line-clamp-3 text-foreground">
                                            {article.title}
                                        </h3>
                                        <div 
                                            className="text-sm text-muted-foreground line-clamp-3 leading-relaxed"
                                            dangerouslySetInnerHTML={{ __html: article.summary }}
                                        />
                                    </div>

                                    <div className="flex-1 flex flex-wrap gap-1 items-end content-end">
                                        {article.tags.slice(0, 3).map((tag, i) => (
                                            <span key={i} className="text-[10px] bg-secondary px-2 py-0.5 rounded text-muted-foreground flex items-center gap-1">
                                                <Tag className="h-2 w-2" />
                                                {tag}
                                            </span>
                                        ))}
                                        {article.tags.length > 3 && (
                                            <span className="text-[10px] text-muted-foreground">+{article.tags.length - 3}</span>
                                        )}
                                    </div>

                                    <div className="pt-4 border-t border-border flex items-center justify-between mt-auto">
                                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                            <Calendar className="h-3.5 w-3.5" />
                                            {new Date(article.publication_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                        </div>
                                        <a 
                                            href={article.url} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            className="text-primary text-sm font-bold flex items-center gap-1 hover:underline"
                                        >
                                            Read More <ExternalLink className="h-3.5 w-3.5" />
                                        </a>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="glass-panel rounded-2xl p-12 text-center">
                        <p className="text-muted-foreground italic">No articles found matching your criteria.</p>
                    </div>
                )}
            </main>
        </div>
    );
}