import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
    label: string;
    value: string;
    trend?: {
        value: string;
        direction: 'up' | 'down' | 'stable';
    };
}

export function StatCard({ label, value, trend }: StatCardProps) {
    const getTrendColor = () => {
        if (!trend) return '';
        switch (trend.direction) {
            case 'up':
                return 'text-emerald-400';
            case 'down':
                return 'text-rose-400';
            default:
                return 'text-muted-foreground';
        }
    };

    const getTrendIcon = () => {
        if (!trend) return null;
        switch (trend.direction) {
            case 'up':
                return <TrendingUp className="h-3 w-3" />;
            case 'down':
                return <TrendingDown className="h-3 w-3" />;
            default:
                return <Minus className="h-3 w-3" />;
        }
    };

    return (
        <div className="glass-panel p-5 rounded-xl">
            <p className="text-muted-foreground text-xs font-medium uppercase tracking-wider">
                {label}
            </p>
            <div className="flex items-end gap-2 mt-1">
                <span className="text-3xl font-bold text-foreground w-[110px] inline-block tabular-nums">{value}</span>
                {trend && (
                    <span className={`flex items-center gap-1 text-xs font-medium mb-1 ${getTrendColor()}`}>
                        {getTrendIcon()}
                        {trend.value}
                    </span>
                )}
            </div>
        </div>
    );
}
