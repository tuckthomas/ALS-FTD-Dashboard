/// <reference types="vite/client" />

import type { DetailedHTMLProps, HTMLAttributes } from 'react';

declare global {
    namespace JSX {
        interface IntrinsicElements {
            'pdbe-molstar': DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> & {
                [key: string]: unknown;
            };
        }
    }
}

export { };
