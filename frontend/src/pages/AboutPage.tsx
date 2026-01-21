import { Github, Database, Activity, Search, Info, Target } from 'lucide-react';

export function AboutPage() {
    return (
        <div className="max-w-[1000px] mx-auto p-6 space-y-12">

            {/* Hero Section */}
            {/* Hero Section */}
            <div className="flex items-center gap-4">
                <div className="p-2 bg-primary/10 rounded-lg shrink-0">
                    <Info className="h-8 w-8 text-primary" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-foreground tracking-tight">
                        Familial ALS & FTD Research Analytics
                    </h1>
                    <p className="text-muted-foreground italic text-sm mt-1">
                        A specialized analytics platform focused on tracking clinical trials for familial
                        (genetic/hereditary) forms of Amyotrophic Lateral Sclerosis and Frontotemporal Dementia.
                    </p>
                </div>
            </div>

            {/* Mission Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-6 rounded-xl space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center text-primary shrink-0">
                            <Database className="w-6 h-6" />
                        </div>
                        <h3 className="text-lg font-semibold text-foreground">Data Integration</h3>
                    </div>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                        We aggregate real-time data from ClinicalTrials.gov, harmonizing complex datasets
                        into a unified schema optimized for research analytics.
                    </p>
                </div>

                <div className="glass-panel p-6 rounded-xl space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="bg-accent/10 w-12 h-12 rounded-lg flex items-center justify-center text-accent shrink-0">
                            <Activity className="w-6 h-6" />
                        </div>
                        <h3 className="text-lg font-semibold text-foreground">Real-time Analytics</h3>
                    </div>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                        Track enrollment trends, trial phases, and geographic distribution. Our dashboards
                        provide instant visibility into the evolving research landscape.
                    </p>
                </div>

                <div className="glass-panel p-6 rounded-xl space-y-4">
                    <div className="flex items-center gap-4">
                        <div className="bg-emerald-500/10 w-12 h-12 rounded-lg flex items-center justify-center text-emerald-500 shrink-0">
                            <Search className="w-6 h-6" />
                        </div>
                        <h3 className="text-lg font-semibold text-foreground">Trial Discovery</h3>
                    </div>
                    <p className="text-muted-foreground text-sm leading-relaxed">
                        Advanced filtering tools help families affected by genetic ALS/FTD, clinicians, and researchers
                        find relevant studies based on status, phase, location, and genetic markers like C9orf72, SOD1, and FUS.
                    </p>
                </div>
            </div>

            {/* Story/Context Section */}
            <div className="glass-panel p-8 rounded-xl border border-border/50">
                <div className="flex items-center gap-4 mb-6">
                    <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center text-primary shrink-0">
                        <Target className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-foreground">Our Mission</h2>
                        <p className="text-muted-foreground text-sm">Why We Built This</p>
                    </div>
                </div>
                <div className="space-y-4 text-muted-foreground leading-relaxed">
                    <p>
                        <strong className="text-foreground">Familial ALS and FTD</strong> are hereditary forms of these devastating
                        neurodegenerative diseases, caused by mutations in genes like C9orf72, SOD1, TARDBP, FUS, and others.
                        Families carrying these mutations face not only the immediate impact of the disease but also the
                        uncertainty of knowing that other family members may be at risk.
                    </p>
                    <p>
                        This platform was created specifically to serve the familial ALS/FTD community. By aggregating
                        and visualizing clinical trial data filtered by genetic markers, we aim to help patients,
                        caregivers, and presymptomatic gene carriers find relevant trials and stay informed about
                        emerging gene-targeted therapies.
                    </p>
                    <p>
                        While the underlying trial data comes from ClinicalTrials.gov and covers all ALS/FTD research,
                        our focus is on making genetic and familial research more accessible to those who need it most.
                    </p>
                </div>
            </div>

            {/* Open Source / Contributing */}
            {/* Open Source / Contributing */}
            <div className="glass-panel p-8 rounded-xl border border-border/50 space-y-6">
                <div className="flex items-center gap-4">
                    <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center text-primary shrink-0">
                        <Github className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-foreground">Open Source</h2>
                        <p className="text-muted-foreground text-sm">Community Driven</p>
                    </div>
                </div>

                <p className="text-muted-foreground leading-relaxed max-w-3xl">
                    This project is open source and community-driven. We welcome contributions from
                    developers, researchers, and advocates to help improve familial ALS/FTD research accessibility.
                </p>

                <div>
                    <a
                        href="https://github.com/tuckthomas/ALS-FTD-Dashboard.git"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-lg hover:shadow-xl translate-y-0 hover:-translate-y-0.5 duration-200"
                    >
                        <Github className="w-5 h-5" />
                        <span>View on GitHub</span>
                    </a>
                </div>
            </div>

            {/* Footer / Disclaimer */}
            <div className="text-center border-t border-border pt-8">
                <p className="text-xs text-muted-foreground">
                    <strong>Disclaimer:</strong> This dashboard is for informational and research purposes only.
                    It does not constitute medical advice. Always consult with a qualified healthcare provider
                    regarding medical conditions or clinical trial participation.
                </p>
            </div>
        </div>
    );
}
