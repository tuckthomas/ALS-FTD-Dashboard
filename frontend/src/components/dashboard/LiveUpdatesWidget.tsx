import { Link } from 'react-router-dom';
import { ArrowRight, Newspaper } from 'lucide-react';

interface NewsItem {
    title: string;
    source: string;
    date: string;
    url: string;
}

interface LiveUpdatesWidgetProps {
    news?: NewsItem[];
}

export function LiveUpdatesWidget({ news }: LiveUpdatesWidgetProps) {
    return (
        <div className="glass-panel p-5 rounded-xl flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                    <div className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse" />
                    Live Updates
                </h3>
                <Link to="/news" className="text-[10px] text-primary hover:underline flex items-center gap-1">
                    View All <ArrowRight className="h-3 w-3" />
                </Link>
            </div>

            <div className="flex-1 space-y-4">
                {news && news.length > 0 ? (
                    news.map((item, i) => (
                        <a 
                            key={i} 
                            href={item.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="block group"
                        >
                            <div className="space-y-1">
                                <span className="text-[10px] font-semibold text-primary bg-primary/10 px-1.5 py-0.5 rounded">
                                    {item.source}
                                </span>
                                <h4 className="text-sm font-medium text-foreground group-hover:text-primary transition-colors line-clamp-2">
                                    {item.title}
                                </h4>
                                <span className="text-[10px] text-muted-foreground">
                                    {item.date}
                                </span>
                            </div>
                        </a>
                    ))
                ) : (
                    <div className="flex flex-col items-center justify-center min-h-[200px] text-center space-y-2 py-4">
                        <Newspaper className="h-8 w-8 text-muted-foreground/50" />
                        <p className="text-xs text-muted-foreground italic">
                            News Aggregator in Development
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
