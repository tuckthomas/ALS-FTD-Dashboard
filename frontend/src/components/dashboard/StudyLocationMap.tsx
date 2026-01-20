import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Loader2, Maximize2, Minimize2, Layers, Map as MapIcon } from 'lucide-react';
import { useTheme } from '../theme/ThemeProvider';

interface SiteData {
    name: string;
    city: string;
    country: string;
    position: [number, number];
    trial_count: number;
    trials: { id: string, title: string }[];
}

interface StudyLocationMapProps {
    data?: SiteData[];
}

export function StudyLocationMap({ data: propData }: StudyLocationMapProps) {
    const [sites, setSites] = useState<SiteData[]>(propData || []);
    const [loading, setLoading] = useState(!propData);
    const { theme } = useTheme();
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [mapLayer, setMapLayer] = useState<'street' | 'satellite'>('street');
    const [showLayerMenu, setShowLayerMenu] = useState(false);
    const mapContainerRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (propData) {
            setSites(propData);
            setLoading(false);
            return;
        }

        const fetchMapData = async () => {
            try {
                const response = await axios.get('/api/analytics/global-map');
                setSites(response.data);
            } catch (error) {
                console.error("Failed to fetch map data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchMapData();
    }, [propData]);

    // Handle fullscreen toggle
    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            mapContainerRef.current?.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable fullscreen mode: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen();
        }
    };

    // Listen for fullscreen changes to update state
    useEffect(() => {
        const handleFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };
        document.addEventListener('fullscreenchange', handleFullscreenChange);
        return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
    }, []);

    // Define tile layers based on theme and selection
    const darkTiles = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
    const lightTiles = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";
    const satelliteTiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";

    const currentTiles = mapLayer === 'satellite'
        ? satelliteTiles
        : (theme === 'dark' ? darkTiles : lightTiles);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[400px] glass-panel rounded-xl">
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
            </div>
        );
    }

    return (
        <div ref={mapContainerRef} className={`glass-panel p-6 rounded-xl relative overflow-hidden flex flex-col transition-all duration-300 ${isFullscreen ? 'fixed inset-0 z-[100] h-screen w-screen rounded-none p-0 bg-background' : 'h-[500px]'}`}>
            {!isFullscreen && (
                <div className="mb-4">
                    <h3 className="text-lg font-bold text-foreground">Global Trial Density Map</h3>
                    <p className="text-muted-foreground text-xs">Geographic distribution of clinical trial sites</p>
                </div>
            )}

            <div className={`flex-1 overflow-hidden border border-border relative z-0 ${isFullscreen ? '' : 'rounded-lg'}`}>
                <MapContainer
                    center={[20, 0]}
                    zoom={2}
                    style={{ height: '100%', width: '100%', background: theme === 'dark' ? '#0f172a' : '#f8fafc' }}
                    scrollWheelZoom={true}
                    attributionControl={false}
                    zoomControl={false}
                >
                    <TileLayer
                        url={currentTiles}
                        attribution={mapLayer === 'satellite' ? 'Esri World Imagery' : 'OpenStreetMap'}
                    />

                    {sites.map((site, index) => (
                        <CircleMarker
                            key={index}
                            center={site.position}
                            pathOptions={{
                                color: '#19c3e6',
                                fillColor: '#19c3e6',
                                fillOpacity: 0.6,
                                weight: 1
                            }}
                            radius={Math.log(site.trial_count + 1) * 3 + 3}
                        >
                            <Tooltip direction="top" offset={[0, -5]} opacity={1}>
                                <div className="text-xs font-bold">{site.city}, {site.country}</div>
                                <div className="text-[10px]">{site.trial_count} trial(s)</div>
                            </Tooltip>
                            <Popup className="custom-popup">
                                <div className="p-1 min-w-[200px]">
                                    <h4 className="font-bold text-sm mb-1 text-foreground">{site.name}</h4>
                                    <div className="text-xs text-slate-600 dark:text-slate-400 mb-2">{site.city}, {site.country}</div>
                                    <div className="max-h-[150px] overflow-y-auto custom-scrollbar">
                                        {site.trials.map(t => (
                                            <div
                                                key={t.id}
                                                className="mb-1 pb-1 border-b border-slate-100 last:border-0 last:mb-0 last:pb-0 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors p-1 rounded"
                                                onClick={() => navigate(`/trials?search=${t.id}`)}
                                            >
                                                <div className="font-semibold text-[10px] text-[#0ea5e9]">{t.id}</div>
                                                <div className="text-[10px] truncate" title={t.title}>{t.title}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </Popup>
                        </CircleMarker>
                    ))}
                </MapContainer>

                {/* Custom Controls Container */}

                {/* Layer Control - Top Right */}
                <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2 items-end">
                    <button
                        onClick={() => setShowLayerMenu(!showLayerMenu)}
                        className="p-2 bg-background/60 backdrop-blur-md border border-border rounded-md shadow-sm hover:bg-accent hover:text-accent-foreground transition-all"
                        title="Change Map Layer"
                    >
                        <Layers className="h-5 w-5" />
                    </button>

                    {showLayerMenu && (
                        <div className="bg-background/80 backdrop-blur-md border border-border rounded-md p-1 flex flex-col gap-1 shadow-lg animate-in fade-in zoom-in-95 duration-200 origin-top-right">
                            <button
                                onClick={() => { setMapLayer('street'); setShowLayerMenu(false); }}
                                className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded-sm transition-colors ${mapLayer === 'street' ? 'bg-[#19c3e6]/20 text-[#19c3e6]' : 'hover:bg-accent hover:text-accent-foreground'}`}
                            >
                                <MapIcon className="h-3 w-3" />
                                Street
                            </button>
                            <button
                                onClick={() => { setMapLayer('satellite'); setShowLayerMenu(false); }}
                                className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded-sm transition-colors ${mapLayer === 'satellite' ? 'bg-[#19c3e6]/20 text-[#19c3e6]' : 'hover:bg-accent hover:text-accent-foreground'}`}
                            >
                                <Layers className="h-3 w-3" />
                                Satellite
                            </button>
                        </div>
                    )}
                </div>

                {/* Fullscreen Button - Bottom Right */}
                <button
                    onClick={toggleFullscreen}
                    className="absolute bottom-4 right-4 z-[1000] p-2 bg-background/60 backdrop-blur-md border border-border rounded-md shadow-sm hover:bg-accent hover:text-accent-foreground transition-all"
                    title={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
                >
                    {isFullscreen ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
                </button>
            </div>
        </div>
    );
}
