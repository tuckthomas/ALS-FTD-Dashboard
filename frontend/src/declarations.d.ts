/// <reference types="react" />

declare namespace JSX {
    interface IntrinsicElements {
        'metabase-dashboard': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
            token?: string;
            'with-title'?: string;
            'with-downloads'?: string;
            theme?: string;
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
