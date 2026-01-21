/// <reference types="react" />

declare namespace JSX {
    interface IntrinsicElements {
        'metabase-dashboard': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
            token?: string;
            'with-title'?: string;
            'with-downloads'?: string;
            theme?: string;
        };
        'pdbe-molstar': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
            'molecule-id'?: string;
            'custom-data-url'?: string;
            'custom-data-format'?: string;
            'visual-style'?: string;
            'hide-controls'?: string;
            'bg-color-r'?: string;
            'bg-color-g'?: string;
            'bg-color-b'?: string;
        };
    }
}


interface Window {
    metabaseConfig: {
        theme: {
            preset: string;
        };
        isGuest: boolean;
        instanceUrl: string;
    };
}
