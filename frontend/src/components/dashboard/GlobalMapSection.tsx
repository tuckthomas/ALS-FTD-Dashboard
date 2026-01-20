import { StudyLocationMap } from "./StudyLocationMap";

interface GlobalMapSectionProps {
    data?: any[]; // Keep prop interface for compatibility but it's now handled internally by the component
}

export function GlobalMapSection({ data }: GlobalMapSectionProps) {
    return (
        <StudyLocationMap data={data} />
    );
}
